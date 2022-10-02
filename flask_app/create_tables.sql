CREATE TABLE IF NOT EXISTS address(
    address_id INT PRIMARY KEY NOT NULL,
    address_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS restaurant_address(
    restaurant_id INT NOT NULL,
    address_id INT NOT NULL
);

CREATE TABLE IF NOT EXISTS restaurant(
    restaurant_id INT PRIMARY KEY NOT NULL,
    restaurant_name VARCHAR NOT NULL,
    restaurant_description VARCHAR(300) NOT NULL,
    restaurant_img VARCHAR
);
