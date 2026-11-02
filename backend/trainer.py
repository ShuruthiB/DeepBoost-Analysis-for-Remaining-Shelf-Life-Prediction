"""Command-line entry point for training the real inventory hybrid model."""

if __package__:
    from .training.train_hybrid import main
else:
    from training.train_hybrid import main


if __name__ == "__main__":
    main()