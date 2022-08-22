def get_image_allowed_extensions():
    return ["jpeg", "jpg", "png"]


def get_model_allowed_extensions():
    return ["h5"]


def allowed_file(filename, extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in extensions
