CREATE TABLE IF NOT EXISTS address(
    address_id INT PRIMARY KEY NOT NULL,
    address_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS restaurant(
    restaurant_id INT PRIMARY KEY NOT NULL,
    restaurant_name VARCHAR NOT NULL,
    restaurant_description VARCHAR(300) NOT NULL,
    restaurant_img VARCHAR
);

CREATE TABLE IF NOT EXISTS test(
    test_id INT PRIMARY KEY NOT NULL,
    test_name VARCHAR NOT NULL
);

INSERT INTO test(test_id, test_name) VALUES(1, 'essa') ON CONFLICT DO NOTHING;