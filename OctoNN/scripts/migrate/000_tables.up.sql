-- public models that were addedd by me
-- can train any model on any dataset by just changing the output layer. need to make a copy of the model and go train it
-- this means that we care about the model's input (and possibly preprocessing)
-- trainings are still stored, but again, can be done on any dataset
-- models can be evaluated on images on any list of images.
-- "type" simply means set of output labels
-- can make a model public?
-- feature vector or not? (just an if in the code)


CREATE TABLE users(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT,
    password TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT username_unique UNIQUE (username),
    CONSTRAINT email_unique UNIQUE (email)
);

-- it remains to be determined if this is necessary
-- somehow these need to be cleaned up
-- CREATE TABLE datatypes(
--     id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
--     outputs INT,
--     labels TEXT[]
-- );

-- If necessary, we can make a datatypes table to associate with each dataset
-- The main folder will contain subfolders with the name of the classifications.
CREATE TABLE datasets(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    location TEXT, -- might be unnecessary
    description TEXT,
    labels TEXT[]
    -- datatype UUID,
    -- CONSTRAINT fk_datatype FOREIGN KEY (datatype) references datatypes (id)
);


-- See how this can be optimized in the future
-- In the UI this should also display input shape
CREATE TABLE models(
    id UUID NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    uploader UUID NOT NULL,
    location TEXT, -- location on disk
    description TEXT,
    createad_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    -- public only means that it can be viewed by other people and copied (as well as the training list)
    public BOOLEAN,
    -- dataset the model was last trained on (maybe not necessary)
    last_trained_on UUID,
    CONSTRAINT fk_author FOREIGN KEY (uploader) REFERENCES users (id),
    CONSTRAINT fk_dataset FOREIGN KEY (last_trained_on) REFERENCES datasets (id)
);

CREATE TABLE trainings(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    model UUID,
    dataset UUID,
    compiler TEXT,
    loss_function TEXT,
    epochs INT,
    accuracy FLOAT[],
    loss_value FLOAT[],
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT fk_model FOREIGN KEY (model) REFERENCES models (id) ON DELETE CASCADE,
    -- cannot delete datasets that were already used for training
    CONSTRAINT fk_dataset FOREIGN KEY (dataset) REFERENCES models(id)
);

-- ready to deploy models
-- CREATE TABLE deployment_models(
--     id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
--     model UUID,
--     user UUID,
--     data BYTEA,
--     public bool,
--     created_at TIMESTAMPTZ DEFAULT now(),
--     CONSTRAINT fk_model FOREIGN KEY (model) REFERENCES models(id)
-- );
