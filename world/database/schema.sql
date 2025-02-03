-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Sectors table for 2D space partitioning
CREATE TABLE sectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    -- Square sector boundaries in parsecs (X-Y plane only)
    x_min FLOAT NOT NULL,
    x_max FLOAT NOT NULL,
    y_min FLOAT NOT NULL,
    y_max FLOAT NOT NULL,
    level INTEGER DEFAULT 0,
    parent_sector_id INTEGER REFERENCES sectors(id),
    -- Add constraints
    CONSTRAINT valid_x_bounds CHECK (x_min < x_max),
    CONSTRAINT valid_y_bounds CHECK (y_min < y_max)
);

-- Create indexes for efficient sector queries
CREATE INDEX idx_sectors_x ON sectors (x_min, x_max);
CREATE INDEX idx_sectors_y ON sectors (y_min, y_max);
CREATE INDEX idx_sectors_hierarchy ON sectors (parent_sector_id, level);

-- Space objects table with spatial representation
CREATE TABLE space_objects (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    object_type VARCHAR(50) NOT NULL,
    -- Using POINTZ for 3D positioning
    position GEOMETRY(POINTZ, 3857) NOT NULL,
    -- Orientation as a normalized vector using POINTZ
    orientation GEOMETRY(POINTZ, 3857) NOT NULL,
    -- Velocity vector using POINTZ for movement prediction
    velocity GEOMETRY(POINTZ, 3857),
    -- Systems status in JSONB for quick updates
    status JSONB NOT NULL DEFAULT '{
        "active": true,
        "cochrane_field": 1.0,
        "shields": {
            "forward": {"strength": 100, "allocation": 0},
            "aft": {"strength": 100, "allocation": 0},
            "port": {"strength": 100, "allocation": 0},
            "starboard": {"strength": 100, "allocation": 0},
            "dorsal": {"strength": 100, "allocation": 0},
            "ventral": {"strength": 100, "allocation": 0}
        }
    }'::jsonb,
    power_systems JSONB NOT NULL DEFAULT '{}'::jsonb,
    sector_id INTEGER REFERENCES sectors(id),
    parent_object_id INTEGER REFERENCES space_objects(id),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Add constraints for proper 3D geometry
    CONSTRAINT enforce_dims_pos CHECK (ST_NDims(position) = 3),
    CONSTRAINT enforce_dims_orient CHECK (ST_NDims(orientation) = 3),
    CONSTRAINT enforce_dims_vel CHECK (ST_NDims(velocity) = 3 OR velocity IS NULL)
);

-- Create spatial indexes for efficient queries
CREATE INDEX idx_space_objects_position ON space_objects USING GIST (position);
CREATE INDEX idx_space_objects_orientation ON space_objects USING GIST (orientation);
CREATE INDEX idx_space_objects_velocity ON space_objects USING GIST (velocity);
CREATE INDEX idx_space_objects_type ON space_objects (object_type);
CREATE INDEX idx_space_objects_sector ON space_objects (sector_id);
CREATE INDEX idx_space_objects_hierarchy ON space_objects (parent_object_id);
CREATE INDEX idx_space_objects_key ON space_objects (key);

-- Function to update sector containment
CREATE OR REPLACE FUNCTION update_sector_containment() 
RETURNS TRIGGER AS $$
BEGIN
    -- Find containing sector based on X-Y position only
    SELECT id INTO NEW.sector_id
    FROM sectors s
    WHERE 
        ST_X(NEW.position) BETWEEN s.x_min AND s.x_max
        AND ST_Y(NEW.position) BETWEEN s.y_min AND s.y_max;

    -- Update cochrane field strength based on Z position
    NEW.status = jsonb_set(
        NEW.status,
        '{cochrane_field}',
        to_jsonb(GREATEST(0.0, 1.0 - abs(ST_Z(NEW.position)) / 500.0))
    );

    -- Update last_updated timestamp
    NEW.last_updated = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic sector updates
CREATE TRIGGER space_object_sector_update
    BEFORE INSERT OR UPDATE OF position ON space_objects
    FOR EACH ROW
    EXECUTE FUNCTION update_sector_containment();

-- Create index on last_updated for efficient updates
CREATE INDEX idx_space_objects_last_updated ON space_objects (last_updated);