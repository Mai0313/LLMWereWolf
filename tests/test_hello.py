from repo_template.cli import main


def test_main():
    hello = main()
    assert hello.name == "Wei"
    assert hello.content == "Hello, World!"
