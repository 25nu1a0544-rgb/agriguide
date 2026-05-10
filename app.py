from flask import Flask, render_template, request
from crop_data import crop_data

app = Flask(__name__)

# ==========================================
# HISTORY STORAGE
# ==========================================
history = []


# ==========================================
# PROFIT CALCULATION FUNCTION
# ==========================================
def calculate_profit(crop):

    data = crop_data[crop]

    income = data["yield_ton_per_acre"] * data["price_per_ton"]

    profit = income - data["investment"]

    return {
        "yield": data["yield_ton_per_acre"],
        "income": income,
        "profit": profit
    }


# ==========================================
# HOME PAGE
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# RESULT PAGE (SMART ENGINE)
# ==========================================
@app.route("/result", methods=["POST"])
def result():

    season = request.form.get("season")
    soil = request.form.get("soil")
    water = request.form.get("water")
    budget = int(request.form.get("budget"))

    # -----------------------------
    # SAVE HISTORY
    # -----------------------------
    history.append({
        "season": season,
        "soil": soil,
        "water": water,
        "budget": budget
    })

    if len(history) > 5:
        history.pop(0)

    # -----------------------------
    # RESULT STRUCTURE
    # -----------------------------
    results = {
        "Crop": {},
        "Vegetable": {},
        "Fruit": {},
        "Herb": {}
    }

    scored_list = []

    # -----------------------------
    # SMART SCORING ENGINE
    # -----------------------------
    for name, data in crop_data.items():

        score = 0

        # Season match
        if season in data["season"]:
            score += 2

        # Soil match
        if soil in data["soil"]:
            score += 2

        # Water match
        if water == data["water_level"]:
            score += 2

        # Budget influence (VERY IMPORTANT)
        if data["investment"] <= budget:
            score += 3
        else:
            score -= 1  # still show but lower rank

        # Profit influence
        profit_data = calculate_profit(name)
        score += profit_data["profit"] / 10000

        scored_list.append((score, name, data, profit_data))

    # -----------------------------
    # SORT BY SCORE (DYNAMIC OUTPUT)
    # -----------------------------
    scored_list.sort(reverse=True, key=lambda x: x[0])

    # -----------------------------
    # DISTRIBUTE INTO CATEGORIES
    # -----------------------------
    for score, name, data, profit_data in scored_list:

        results[data["category"]][name] = {
            "data": data,
            "profit": profit_data,
            "score": round(score, 2)
        }

    # -----------------------------
    # BEST CROP SELECTION
    # -----------------------------
    if scored_list:
        best_crop = {
            "name": scored_list[0][1],
            "profit": scored_list[0][3]["profit"]
        }
    else:
        best_crop = None

    # -----------------------------
    # RENDER OUTPUT
    # -----------------------------
    return render_template(
        "result.html",
        results=results,
        season=season,
        soil=soil,
        water=water,
        budget=budget,
        history=history,
        best_crop=best_crop
    )


# ==========================================
# CLEAR HISTORY
# ==========================================
@app.route("/clear-history")
def clear_history():
    history.clear()
    return render_template("index.html")


# ==========================================
# RUN APP
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)