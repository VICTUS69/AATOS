import time

def get_green_time(cars):
    """
    Rule-based timing: more cars → longer green.
    """
    if cars == 0:
        return 0
    elif cars == 1:
        return 4
    else:
        return min(60, 4 + (cars - 1) * 3)  # cap at 60 sec

def traffic_junction_controller(counts):
    directions = ["North", "East", "South", "West"]

    for dir in directions:
        cars = counts[dir]
        green_time = get_green_time(cars)

        if green_time == 0:
            print(f"{dir}: 🚫 No cars → Skipping")
            continue

        print(f"{dir}: 🚗 {cars} cars → Green {green_time}s")
        time.sleep(green_time)

        print(f"{dir}: 🟡 Yellow 2s")
        time.sleep(2)

        print(f"{dir}: 🔴 Red\n")

    print("🔄 Cycle complete.\n")
