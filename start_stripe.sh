stripe listen --forward-to backend-1:8000/webhook/ &
STRIPE_LISTEN_PID=$!

sleep 0.2

STRIPE_ENDPOINT_SECRET=$(stripe listen --print-secret)
echo "The value of STRIPE_ENDPOINT_SECRET accepted"

echo $STRIPE_ENDPOINT_SECRET > /shared/stripe_endpoint_secret.txt
export STRIPE_ENDPOINT_SECRET

wait $STRIPE_LISTEN_PID
