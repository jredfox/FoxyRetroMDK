find "$1" -type f -name "*.sh" | while read -r file; do
    echo "Patching python call $file"
    sed -i -e 's/python/python2.7/g' "$file"
done