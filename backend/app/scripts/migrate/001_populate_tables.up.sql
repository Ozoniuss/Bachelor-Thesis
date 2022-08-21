INSERT INTO users (id, username, password, email, created_at, updated_at) VALUES 
('01232321-3222-2122-bb21-6a21abab1121', 'root', '$2b$12$lqa7NbGmcIS5kdcvGkmyWuCK5y0SvBT..GUlHJ44fhSdGgJyiwG9G', 'root@octonn.com', TIMESTAMPTZ '2022-07-21 10:23:54+03', TIMESTAMPTZ '2022-07-21 10:23:54+03'),
('261b8ee5-02e4-4733-b377-dd17732006d8', 'admin', '$2b$12$mrbn/oZTML9aPl5TdLFsh.cZ1OyMmedLPsXG8IjXxzpcNBTE.nywS', 'admin@octonn.com', TIMESTAMPTZ '2022-07-21 10:24:54+03', TIMESTAMPTZ '2022-07-21 10:24:54+03'),
('c7261dfc-d769-442c-964b-834371ff2e18', 'test', '$2b$12$0vBmDCYMutUJYwPPECU2wupE1s7yH1KHWD0xsIjI4GWhMOg24gdxK', 'test@octonn.com', TIMESTAMPTZ '2022-07-21 10:25:54+03', TIMESTAMPTZ '2022-07-21 10:25:54+03');

INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a294f', 'cats-vs-dogs', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('3a3b10e2-14bb-41bb-f1a2-1a2a3a4bd2d3', 'five-flowers','A decent flowers dataset with 3600 images and 5 different categories.', '{"daisy", "dandelion", "roses", "sunflowers", "tulips"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2940', 'cats-vs-dogs-2', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2941', 'cats-vs-dogs-3', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2942', 'cats-vs-dogs-4', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2943', 'cats-vs-dogs-5', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2944', 'cats-vs-dogs-6', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2945', 'cats-vs-dogs-7', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2946', 'cats-vs-dogs-8', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2947', 'cats-vs-dogs-9', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2948', 'cats-vs-dogs-10', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a2949', 'cats-vs-dogs-11', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a294a', 'cats-vs-dogs-12', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');
INSERT INTO datasets (id, name, description, labels) VALUES 
('0f8ec842-52b4-46b1-8dc6-fa71e60a294b', 'cats-vs-dogs-13', 'A pretty large dataset with 25000 images of cats and dogs.', '{"cats", "dogs"}');

INSERT INTO models (id, name, belongs_to , description, created_at, updated_at, public, last_trained_on, current_prediction_labels) VALUES 
('2c87dd1a-ca57-4f6a-819f-bcf3cdd47642', 'test_root', '01232321-3222-2122-bb21-6a21abab1121', 'This model will always be in the database for testing purposes', TIMESTAMPTZ '2022-07-21 10:42:51+03', TIMESTAMPTZ '2022-07-21  10:42:51+03', true, '0f8ec842-52b4-46b1-8dc6-fa71e60a294f', '{"cats", "dogs"}'),
('34a34a21-5671-0aa2-ff31-a2645cd12fe3', 'test_private_root', '01232321-3222-2122-bb21-6a21abab1121', 'This model will always be in the database for testing purposes. It is the same model trained on cats-vs-dogs, but it is private.', TIMESTAMPTZ '2022-07-21 10:42:51+03', TIMESTAMPTZ '2022-07-21  10:42:51+03', false, '0f8ec842-52b4-46b1-8dc6-fa71e60a294f', '{"cats", "dogs"}'),
('1133443a-5dcf-4d7a-81af-819077907c0b', 'test_test', 'c7261dfc-d769-442c-964b-834371ff2e18', 'This model is always in the database and belongs to the test user.', TIMESTAMPTZ '2022-07-21 10:42:51+03', TIMESTAMPTZ '2022-07-21  10:42:51+03', false, '0f8ec842-52b4-46b1-8dc6-fa71e60a294f', '{"cats", "dogs"}');
