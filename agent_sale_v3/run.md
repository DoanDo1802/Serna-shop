cd "/Users/doando/Documents/agent_sale_v3/agent_sale"
uv run run_crew

ngrok http 8000

cd agent_sale
uv run python src/agent_sale/api.py
https://a157-2405-4802-1bb7-af0-3054-1cd0-ed63-5735.ngrok-free.app/chat/simple