# Contributing

## General guidelines

### Use of generative AI is banned
Generative AI uses training data [based on plagiarism and piracy](https://web.archive.org/web/20250000000000*/https://www.theatlantic.com/technology/archive/2025/03/libgen-meta-openai/682093/), has [significant environmental costs associated with it](https://doi.org/10.21428/e4baedd9.9070dfe7), and [generates fundamentally insecure code](https://doi.org/10.1007/s10664-024-10590-1). GenAI is not ethically built, ethical to use, nor safe to use for programming applications. When caught, you will be permanently banned from contributing to the project, and any prior contributions will be checked and potentially reverted. 

### Testing policy

As a general rule, as much code as possible should be tested. If you add a new feature, please consider writing tests for the functionality as well. You can opt not to add tests, but doing so is strongly encouraged.

If you change functionality, existing tests that no longer work must be fixed.

## Development setup

Run `pip3 install -r requirements.txt` for the dependencies. `requirements.txt` contains some additional dependencies than `pyproject.toml` does.

### Running tests

To run the tests, you need some form of Chromedriver installed on your system. Standard chromium seems to work fine on my system, so it doesn't have to be full googlified chrome. You can run the tests with:
```bash
python3 -m pytest
```

This runs both standard and E2E tests. These are automatically run when you make a pull request, but because GitHub requires workflow runs to be approved before they're run, it's strongly recommended you don't use pull requests for rapid feedback, as I will not be sitting ready to push the button to run it immediately.
