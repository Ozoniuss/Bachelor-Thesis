INSERT INTO users (id, username, password, email, created_at, updated_at) VALUES 
('01232321-3222-2122-bb21-6a21abab1121', 'root', '$2b$12$lqa7NbGmcIS5kdcvGkmyWuCK5y0SvBT..GUlHJ44fhSdGgJyiwG9G', 'root@octonn.com', TIMESTAMPTZ '2022-07-21 10:23:54+03', TIMESTAMPTZ '2022-07-21 10:23:54+03'),
('261b8ee5-02e4-4733-b377-dd17732006d8', 'admin', '$2b$12$mrbn/oZTML9aPl5TdLFsh.cZ1OyMmedLPsXG8IjXxzpcNBTE.nywS', 'admin@octonn.com', TIMESTAMPTZ '2022-07-21 10:24:54+03', TIMESTAMPTZ '2022-07-21 10:24:54+03'),

--password: test
('c7261dfc-d769-442c-964b-834371ff2e18', 'alex', '$2b$12$0vBmDCYMutUJYwPPECU2wupE1s7yH1KHWD0xsIjI4GWhMOg24gdxK', 'alexbledea_2000@yahoo.com', TIMESTAMPTZ '2022-07-21 10:25:54+03', TIMESTAMPTZ '2022-07-21 10:25:54+03');

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

INSERT INTO models (id, name, belongs_to , description, created_at, updated_at, public, last_trained_on, current_prediction_labels, param_count) VALUES 
('2c87dd1a-ca57-4f6a-819f-bcf3cdd47642', 'cats_vs_dogs', '01232321-3222-2122-bb21-6a21abab1121', 'A medium-size model attempting to distinguish between cats and dogs.', TIMESTAMPTZ '2022-07-21 10:42:51+03', TIMESTAMPTZ '2022-07-21  10:42:51+03', true, '0f8ec842-52b4-46b1-8dc6-fa71e60a294f', '{"cats", "dogs"}', 420802),
('34a34a21-5671-0aa2-ff31-a2645cd12fe3', 'cats_vs_dogs_private', '01232321-3222-2122-bb21-6a21abab1121', 'A private copy of the medium-size model attempting to distinguish between cats and dogs.', TIMESTAMPTZ '2022-07-23 8:30:10+03', TIMESTAMPTZ '2022-07-23 8:30:10+03', false, '0f8ec842-52b4-46b1-8dc6-fa71e60a294f', '{"cats", "dogs"}', 420802),
('9b06f9d6-089b-4253-936b-3e5d276171d7', 'five_flowers_mobilenet', '01232321-3222-2122-bb21-6a21abab1121', 'A model based on the mobilenet-v2 feature vector trained to classify flowers', TIMESTAMPTZ '2022-07-23 8:30:10+03', TIMESTAMPTZ '2022-07-25 7:40:11+03', true, '3a3b10e2-14bb-41bb-f1a2-1a2a3a4bd2d3', '{"daisy", "dandelion", "roses", "sunflowers", "tulips"}', 420802),
('286ff250-d22b-4333-9f66-587fc0a07a40', 'my first model', 'c7261dfc-d769-442c-964b-834371ff2e18', 'A random model that does not do much.', TIMESTAMPTZ '2022-08-15 11:13:10+03', TIMESTAMPTZ '2022-08-15 11:13:10+03', false, null, '{"car", "van", "truck"}', 387);

INSERT INTO trainings(id, model, dataset, epochs, accuracy, loss, val_accuracy, val_loss, notes, created_at) VALUES 
('1050e321-6656-a2cd-ffa8-2be57521990a', '2c87dd1a-ca57-4f6a-819f-bcf3cdd47642', '0f8ec842-52b4-46b1-8dc6-fa71e60a294f', 15, '{0.5953124761581421, 0.7165625095367432, 0.7871875166893005, 0.8240625262260437, 0.8637499809265137, 0.895312488079071, 0.9181249737739563, 0.9490625262260437, 0.9634374976158142, 0.9759374856948853, 0.9837499856948853, 0.9918749928474426, 0.9950000047683716, 0.9965624809265137, 0.9984375238418579}', '{0.6695745587348938, 0.5693082213401794, 0.4852246046066284, 0.41513678431510925, 0.3490840792655945, 0.28639233112335205, 0.24147047102451324, 0.18965789675712585, 0.1531011313199997, 0.11961064487695694, 0.09635728597640991, 0.07239199429750443, 0.05723385512828827, 0.04396429657936096, 0.034079503268003464}','{0.7024999856948853, 0.7200000286102295, 0.7350000143051147, 0.7049999833106995, 0.7400000095367432, 0.7450000047683716, 0.7387499809265137, 0.7337499856948853, 0.731249988079071, 0.7287499904632568, 0.7350000143051147, 0.7262499928474426, 0.7212499976158142, 0.7124999761581421, 0.7237499952316284}', '{0.6057329773902893, 0.5553666949272156, 0.5406650304794312, 0.5652962327003479, 0.5253687500953674, 0.5210543274879456, 0.5392249822616577, 0.5578402876853943, 0.5970963835716248, 0.6135981678962708, 0.6611461043357849, 0.678925633430481, 0.7324303388595581, 0.8567837476730347, 0.8251623511314392}', 'Great performance on training dataset, but seems to be a bit overfitted.',  TIMESTAMPTZ '2022-07-21 12:45:56+03'),
('3aeb3062-989f-43c5-acab-5ebd48bcba9b', '9b06f9d6-089b-4253-936b-3e5d276171d7', '3a3b10e2-14bb-41bb-f1a2-1a2a3a4bd2d3', 10, '{0.7864148020744324, 0.9026516675949097, 0.9346168041229248, 0.9516890645027161, 0.9640392065048218, 0.9709407687187195, 0.9803850054740906, 0.9822012186050415, 0.988739550113678, 0.9916454553604126}', '{0.5854572057723999, 0.2914886772632599, 0.21706950664520264, 0.1733347326517105, 0.14203079044818878, 0.11790449172258377, 0.09840086847543716, 0.083441823720932, 0.07040262222290039, 0.06090030074119568}','{0.8625954389572144, 0.885496199131012, 0.8865866661071777, 0.8876771926879883, 0.8898582458496094, 0.8909487724304199, 0.8887677192687988, 0.8898582458496094, 0.8920392394065857, 0.8909487724304199}', '{0.3696424067020416, 0.3192885220050812, 0.31946903467178345, 0.3193841576576233, 0.3136984407901764, 0.3104957044124603, 0.30714938044548035, 0.32299405336380005, 0.3170499801635742, 0.33137616515159607}', 'Pretty good overall performance in just 10 epochs, seems not to be overfitting.',  TIMESTAMPTZ '2022-07-26 11:11:03+03');