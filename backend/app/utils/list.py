def same_labels(labels_m: list[str], labels_d: list[str]) -> bool:
    """
    Checks whether two lists of labels (one from the model and one from the
    dataset) have the same labels.
    """
    return set(labels_m) == set(labels_d)
