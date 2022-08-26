CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE users(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT username_unique UNIQUE (username),
    CONSTRAINT email_unique UNIQUE (email)
);

CREATE TRIGGER set_timestamp_user
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- The main folder will contain subfolders with the name of the classifications.
CREATE TABLE datasets(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    labels TEXT[],
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT name_unique UNIQUE (name)
);


CREATE TABLE models(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    belongs_to UUID NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    -- public only means that it can be viewed by other people and copied (as well as the training list)
    public BOOLEAN,
    -- dataset the model was last trained on (maybe not necessary)
    last_trained_on UUID,
    -- models might not reference a dataset, but it's still necessary for the
    -- user to provide labels in order to make predictions.
    current_prediction_labels TEXT[] NOT NULL,
    param_count INTEGER NOT NULL,
    CONSTRAINT fk_author FOREIGN KEY (belongs_to) REFERENCES users (id),
    CONSTRAINT fk_dataset FOREIGN KEY (last_trained_on) REFERENCES datasets (id)
);

CREATE TRIGGER set_timestamp_model
BEFORE UPDATE ON models
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TABLE trainings(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    model UUID NOT NULL,
    dataset UUID NOT NULL,
    epochs INTEGER NOT NULL,
    accuracy FLOAT[] NOT NULL,
    loss FLOAT[] NOT NULL,
    val_accuracy FLOAT[],
    val_loss FLOAT[],
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT fk_model FOREIGN KEY (model) REFERENCES models (id) ON DELETE CASCADE,
    -- cannot delete datasets that were already used for training
    CONSTRAINT fk_dataset FOREIGN KEY (dataset) REFERENCES datasets (id)
);
