-- Design Ref: §3.3 — Database Schema
CREATE TYPE restaurant_status AS ENUM ('VISITED', 'WANT_TO_GO');

CREATE TABLE restaurants (
    id BIGSERIAL PRIMARY KEY,
    google_place_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    status restaurant_status NOT NULL,
    my_rating SMALLINT CHECK (my_rating BETWEEN 1 AND 5),
    memo TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE restaurant_tags (
    restaurant_id BIGINT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (restaurant_id, tag_id)
);

CREATE INDEX idx_restaurants_status ON restaurants(status);
