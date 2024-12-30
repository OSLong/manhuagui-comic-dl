echo "==============================================="
echo "= Export Current Environment "
echo "==============================================="
if [ -x "$(command -v pip)" ]; then
    echo "Export Pip Environment ..."
    pip freeze > requirements.txt
fi

if [ -x "$(command -v conda)" ]; then
    echo "Export Conda Environment ..."
    conda export -n manhuagui | head -n -1 > conda-environments.yaml
fi

