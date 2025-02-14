#!/bin/sh

echo "TOKENS=$TOKENS"

mkdir -p data

# Create JSON start
cat > data/result.json << EOF
{
    "scores": {
EOF

# Process each token using simple sh syntax
for token in $(echo "$TOKENS" | tr ',' '\n'); do
    [ -z "$token" ] && continue
    cat >> data/result.json << EOF
        "$token": $(( $(od -An -N2 -i /dev/urandom) % 101 )),
EOF
done

# Remove last comma and close JSON (busybox compatible)
sed -i '$ s/,$//' data/result.json
cat >> data/result.json << EOF
    }
}
EOF

touch data/replay.dat

sleep 10
