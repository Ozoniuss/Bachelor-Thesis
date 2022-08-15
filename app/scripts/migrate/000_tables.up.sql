
CREATE TABLE users(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
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
    location TEXT NOT NULL, -- location on disk
    description TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    -- public only means that it can be viewed by other people and copied (as well as the training list)
    public BOOLEAN,
    -- dataset the model was last trained on (maybe not necessary)
    last_trained_on UUID,
    current_prediction_labels TEXT[],
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
