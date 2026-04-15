from flask import Flask, render_template, request, redirect, flash, url_for
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


def send_email_report(to_email, report_data):
    print("📨 send_email_report CALLED")
    print("TO:", to_email)
    print("EMAIL_ADDRESS:", EMAIL_ADDRESS)
    print("EMAIL_PASSWORD:", EMAIL_PASSWORD)
    print("TO:", to_email)
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your Finance Report 💸'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg.set_content(report_data)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_type = request.form.get("form_type")

        # ---------------- CALCULATION FORM ----------------
        if form_type == "calc":
            try:
                income = int(request.form["income"])
                food = int(request.form["food"])
                rent = int(request.form["rent"])
                clothes = int(request.form["clothes"])
                bills = int(request.form["bills"])
                others = int(request.form["others"])
                tips_choice = request.form.get("tips")

                if income == 0:
                    flash("⚠️ Income cannot be zero.")
                    return render_template("index.html")

                total_expenses = food + rent + clothes + bills + others
                savings = income - total_expenses

                p1 = (food / income) * 100
                p2 = (rent / income) * 100
                p3 = (clothes / income) * 100
                p4 = (bills / income) * 100
                p5 = (others / income) * 100
                p6 = (savings / income) * 100

                messages = []
                if savings < 0:
                    messages.append("You are spending more than your earnings.")
                if p6 < 10:
                    messages.append("Your savings are below 10%! Try to control your expenses.")
                if p6 > 40:
                    messages.append("You're spending wisely. Great job!")

                tip_summary = None

                if tips_choice == "yes":
                    percentages = [
                        (p1, "Food"),
                        (p2, "Rent"),
                        (p3, "Clothes"),
                        (p4, "Bills"),
                        (p5, "Others")
                    ]

                    sorted_percentages = sorted(percentages, key=lambda x: x[0], reverse=True)
                    max_category = sorted_percentages[0][1]
                    min_category = sorted_percentages[-1][1]

                    tips = []
                    tips.append(f"You spend the most on <b>{max_category}</b> and the least on <b>{min_category}</b>.")

                    for percent, category in percentages:
                        if percent > 35:
                            tips.append(f"You're spending a lot on <b>{category}</b>. Consider reducing it.")
                        elif percent < 10:
                            tips.append(f"Good job! Your <b>{category}</b> expenses are well managed.")
                        elif 10 <= percent <= 20:
                            tips.append(f"<b>{category}</b> expenses are moderate. Keep monitoring.")

                    tip_summary = "<ul>" + "".join([f"<li>{tip}</li>" for tip in tips]) + "</ul>"

                report_text = f"""Hi there 👋,

Here is your Finance Tracker Report:

Income: ₹{income}
Food: ₹{food} ({p1:.2f}%)
Rent: ₹{rent} ({p2:.2f}%)
Clothes: ₹{clothes} ({p3:.2f}%)
Phone Bills: ₹{bills} ({p4:.2f}%)
Other Expenses: ₹{others} ({p5:.2f}%)

Savings: ₹{savings} ({p6:.2f}%)

Thanks for using our app! 💸
"""

                return render_template(
                    "index.html",
                    income=income,
                    food=food,
                    rent=rent,
                    clothes=clothes,
                    bills=bills,
                    others=others,
                    savings=savings,
                    p1=round(p1, 2),
                    p2=round(p2, 2),
                    p3=round(p3, 2),
                    p4=round(p4, 2),
                    p5=round(p5, 2),
                    p6=round(p6, 2),
                    messages=messages,
                    tip_summary=tip_summary,
                    report_text=report_text,
                    show_email_section=True
                )

            except Exception as e:
                flash(f"⚠️ Something went wrong: {str(e)}")
                return render_template("index.html")

        # ---------------- EMAIL FORM ----------------
        elif form_type == "email":
            try:
                email = request.form.get("email")

                income = int(request.form["income"])
                food = int(request.form["food"])
                rent = int(request.form["rent"])
                clothes = int(request.form["clothes"])
                bills = int(request.form["bills"])
                others = int(request.form["others"])

                total_expenses = food + rent + clothes + bills + others
                savings = income - total_expenses

                report_text = f"""Hi there 👋,

Here is your Finance Tracker Report:

Income: ₹{income}
Food: ₹{food}
Rent: ₹{rent}
Clothes: ₹{clothes}
Bills: ₹{bills}
Others: ₹{others}

Savings: ₹{savings}

Thanks for using our app! 💸
"""

                if send_email_report(email, report_text):
                    flash("📧 Report sent successfully!")
                else:
                    flash("❌ Failed to send report. Please try again.")

                return redirect(url_for("index"))

            except Exception as e:
                flash(f"⚠️ Email error: {str(e)}")
                return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
