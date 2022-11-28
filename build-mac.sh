rm -rf dist/*
pyinstaller main.py --name gl2f-tbl --clean --noconsole
cd dist
zip -r macos.zip gl2f-tbl.app
cd ..
