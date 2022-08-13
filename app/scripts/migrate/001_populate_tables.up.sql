INSERT INTO users (id, username, password, email, created_at, updated_at) VALUES 
('01232321-3222-2122-bb21-6a21abab1121', 'root', '$2a$12$.N3GwRN36fsxhosxu8haHOh5e3YU6jfTZYaiL5D0osBMBl7tQeCrm', 'root@octonn.com', TIMESTAMPTZ '2022-07-21 10:23:54+03', TIMESTAMPTZ '2022-07-21 10:23:54+03');

INSERT INTO datasets (id, name, location, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a294f', 'cats-vs-dogs', 'C:\\personal projects\\Bachelor-Thesis\\datasets\\cats-vs-dogs)', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');

INSERT INTO models (id, name, uploader, location, description, created_at, updated_at, public) VALUES 
('2c87dd1a-ca57-4f6a-819f-bcf3cdd47642', 'test', '01232321-3222-2122-bb21-6a21abab1121', 'C:\\personal projects\\Bachelor-Thesis\\models\\root\\test.h5', 'This model will always be in the database for testing purposes', TIMESTAMPTZ '2022-07-21 10:42:51+03', TIMESTAMPTZ '2022-07-21  10:42:51+03', true);
