from traffic_yolo import get_car_counts
from traffic_controller import traffic_junction_controller
# from traffic_llm import llm_decision  # Uncomment if using LLM

def run_system(use_llm=False):
    counts = get_car_counts()  # Get YOLO car counts

    if use_llm:
        print("🤖 Using LLM for decisions...")
        # timings = llm_decision(counts)
        # print("LLM decided:", timings)
    else:
        print("⚡ Using Rule-Based Controller...")
        traffic_junction_controller(counts)

if __name__ == "__main__":
    run_system(use_llm=False)
