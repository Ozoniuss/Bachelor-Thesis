/* 
For start, everything should be publicly available, except models. Models can
be public, in which case other users can copy them and train them.
*/

CREATE TABLE architectures(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ,
    content JSON,
    description TEXT,
    CONSTRAINT name_unique UNIQUE (name)
);

CREATE TABLE users(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT,
    password TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT username_unique UNIQUE (username)
);

CREATE TABLE datasets(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    location TEXT,
    description TEXT
);

CREATE TABLE models(
    id UUID NOT NULL PRIMARY KEY,
    architecture UUID,
    parameters BYTEA,
    description TEXT,
    author UUID,
    createad_at TIMESTAMPTZ DEFAULT now(),
    public BOOLEAN,
    CONSTRAINT fk_architecture FOREIGN KEY (architecture) REFERENCES architectures(id),
    CONSTRAINT fk_author FOREIGN KEY (author) REFERENCES users(id)
);

CREATE TABLE trainings(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    initial_model UUID,
    resulting_model UUID,
    dataset UUID,
    optimizer TEXT,
    loss TEXT,
    metrics TEXT[],
    epochs INT,
    accuracy FLOAT[],
    createad_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT fk_initial_model FOREIGN KEY(initial_model) REFERENCES models(id),
    CONSTRAINT fk_resulting_model FOREIGN KEY(resulting_model) REFERENCES models(id),
    CONSTRAINT fk_dataset FOREIGN KEY(dataset) REFERENCES models(id)
);

CREATE TABLE deployment_models(
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    model UUID,
    data BYTEA,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT fk_model FOREIGN KEY(model) REFERENCES models(id)
);
