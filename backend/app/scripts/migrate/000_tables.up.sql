
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

-- The main folder will contain subfolders with the name of the classifications.
CREATE TABLE datasets(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    location TEXT,
    description TEXT,
    labels TEXT[],
    created_at TIMESTAMPTZ,
    CONSTRAINT name_unique UNIQUE (name)
);


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
    -- models might not reference a dataset, but it's still necessary for the
    -- user to provide labels in order to make predictions.
    current_prediction_labels TEXT[] NOT NULL,
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
    created_at TIMESTAMPTZ,
    CONSTRAINT fk_model FOREIGN KEY (model) REFERENCES models (id) ON DELETE CASCADE,
    -- cannot delete datasets that were already used for training
    CONSTRAINT fk_dataset FOREIGN KEY (dataset) REFERENCES models(id)
);
