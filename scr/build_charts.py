import os
import io
import base64
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = "DejaVu Sans"

out_dir = "data_processed"
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(os.path.join(out_dir, "passport_debt_rf_2020_2022.csv"))
df["Код_строки"] = df["Код_строки"].astype(str).str.strip()


def save_chart_base64(fig, filename):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=140)
    buf.seek(0)
    b64_str = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(b64_str)
    print(f"Сохранен файл: {out_path} (длина строки: {len(b64_str)} символов)")


# --- ГРАФИК 1. ОБЩАЯ ДИНАМИКА ЗАДОЛЖЕННОСТИ В РФ (МЛРД РУБ.) ---
df_823 = df[df["Код_строки"] == "823"].sort_values("Год").copy()
years_1 = df_823["Год"].astype(str)
x1 = range(len(years_1))
w1 = 0.25

total_1 = df_823["Всего_млн_руб"] / 1000
unsettled_1 = df_823["Недоимка_и_пени_млн_руб"] / 1000
suspended_1 = df_823["Приостановленные_млн_руб"] / 1000

fig1, ax1 = plt.subplots(figsize=(10, 4.8))
b1_1 = ax1.bar([i - w1 for i in x1], total_1, w1, label="Совокупный долг (с учетом взносов)", color="#2C4D75")
b1_2 = ax1.bar(x1, unsettled_1, w1, label="Недоимка и пени", color="#4F81BD")
b1_3 = ax1.bar([i + w1 for i in x1], suspended_1, w1, label="Приостановленный к взысканию долг", color="#B8C4D0")

for bars in (b1_1, b1_2, b1_3):
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(
            f"{h:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#222222",
        )

ax1.set_title("Динамика налоговой задолженности в РФ за 2020–2022 гг. (млрд руб.)", fontsize=12, fontweight="bold", pad=18, color="#222222")
ax1.set_xticks(list(x1))
ax1.set_xticklabels(years_1, fontsize=11, color="#222222")
ax1.set_ylim(0, 2850)
ax1.tick_params(axis="y", labelsize=9.5, colors="#555555")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["left"].set_color("#CCCCCC")
ax1.spines["bottom"].set_color("#CCCCCC")
ax1.legend(frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=10)
plt.tight_layout()

save_chart_base64(fig1, "chart1_base64.txt")


# --- ГРАФИК 2. СТРУКТУРА ЗАДОЛЖЕННОСТИ ПО ОСНОВНЫМ НАЛОГАМ И ВЗНОСАМ (СОСТАВНАЯ, БЕЗ ОСИ Y) ---
df["Всего_млрд"] = df["Всего_млн_руб"] / 1000
piv_2 = df[df["Код_строки"].isin(("806", "804", "822", "807"))].pivot(index="Год", columns="Код_строки", values="Всего_млрд").sort_index()

years_2 = piv_2.index.astype(str)
vat = piv_2.get("806")
profit = piv_2.get("804")
insurance = piv_2.get("822")
ndpi = piv_2.get("807")

fig2, ax2 = plt.subplots(figsize=(10, 5))
w2 = 0.48
ax2.bar(years_2, vat, w2, label="НДС", color="#2C4D75")
ax2.bar(years_2, profit, w2, bottom=vat, label="Налог на прибыль", color="#4F81BD")
ax2.bar(years_2, insurance, w2, bottom=vat + profit, label="Страховые взносы", color="#8EA9DB")
ax2.bar(years_2, ndpi, w2, bottom=vat + profit + insurance, label="НДПИ", color="#B8C4D0")

for i in range(len(years_2)):
    v_val = vat.iloc[i]
    p_val = profit.iloc[i]
    ins_val = insurance.iloc[i]
    n_val = ndpi.iloc[i]

    ax2.text(i, v_val / 2, f"{v_val:.1f}", ha="center", va="center", color="white", fontweight="bold", fontsize=9.5)
    ax2.text(i, v_val + p_val / 2, f"{p_val:.1f}", ha="center", va="center", color="white", fontweight="bold", fontsize=9.5)
    ax2.text(i, v_val + p_val + ins_val / 2, f"{ins_val:.1f}", ha="center", va="center", color="#222222", fontweight="bold", fontsize=9.5)
    ax2.text(i, v_val + p_val + ins_val + n_val / 2, f"{n_val:.1f}", ha="center", va="center", color="#222222", fontweight="bold", fontsize=8.5)

ax2.set_title("Структура задолженности РФ по ключевым налогам и взносам за 2020–2022 гг. (млрд руб.)", fontsize=11.5, fontweight="bold", pad=18, color="#222222")
ax2.set_ylim(0, 1650)
ax2.yaxis.set_visible(False)
ax2.tick_params(axis="x", labelsize=11, colors="#222222")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)
ax2.spines["bottom"].set_color("#CCCCCC")
ax2.legend(frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=10)
plt.tight_layout()

save_chart_base64(fig2, "chart2_base64.txt")


# --- ГРАФИК 3. ДИНАМИКА ПО КАТЕГОРИЯМ НАЛОГОВ И ОТСРОЧКАМ (С ИНВЕРСИЕЙ ПАЛИТРЫ) ---
piv_3 = df[df["Код_строки"].isin(("818", "812", "808"))].pivot(index="Год", columns="Код_строки", values="Всего_млрд").sort_index()
years_3 = piv_3.index.astype(str)
x3 = range(len(years_3))
w3 = 0.20

peni_3 = piv_3.get("818")
reg_3 = piv_3.get("812")
ndfl_3 = piv_3.get("808")
def_3 = df_823["Отсроченные_млн_руб"] / 1000

fig3, ax3 = plt.subplots(figsize=(10.5, 5))
b3_1 = ax3.bar([i - 1.5 * w3 for i in x3], peni_3, w3, label="Пени и налоговые санкции", color="#B8C4D0")
b3_2 = ax3.bar([i - 0.5 * w3 for i in x3], reg_3, w3, label="Региональные налоги и сборы", color="#8EA9DB")
b3_3 = ax3.bar([i + 0.5 * w3 for i in x3], def_3, w3, label="Отсроченные и рассроченные платежи", color="#4F81BD")
b3_4 = ax3.bar([i + 1.5 * w3 for i in x3], ndfl_3, w3, label="НДФЛ", color="#2C4D75")

for bars in (b3_1, b3_2, b3_3, b3_4):
    for bar in bars:
        h = bar.get_height()
        ax3.annotate(
            f"{h:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#222222",
        )

ax3.set_title("Динамика задолженности РФ по пеням, НДФЛ, региональным налогам и отсрочкам (млрд руб.)", fontsize=11.5, fontweight="bold", pad=18, color="#222222")
ax3.set_xticks(list(x3))
ax3.set_xticklabels(years_3, fontsize=11, color="#222222")
ax3.set_ylim(0, 660)
ax3.tick_params(axis="y", labelsize=9.5, colors="#555555")
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.spines["left"].set_color("#CCCCCC")
ax3.spines["bottom"].set_color("#CCCCCC")
ax3.legend(frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9.5)
plt.tight_layout()

save_chart_base64(fig3, "chart3_base64.txt")
print("Все три общероссийских графика успешно перерисованы и сохранены в base64.")
