from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64


app = Flask(__name__)

df = pd.read_csv('data/ai_job_market.csv')
print(df.columns)

df[['min_salary', 'max_salary']] = df['salary_range_usd'].str.split('-', expand=True)
df.drop(['salary_range_usd'], axis=1, inplace=True)
df['min_salary'] = pd.to_numeric(df['min_salary'], errors='coerce')
df['max_salary'] = pd.to_numeric(df['max_salary'], errors='coerce')
df['avg_salary'] = (df['max_salary'] + df['min_salary'])/2

@app.route('/')
def home():
    total_jobs = len(df)
    avg_salary = round(df['avg_salary'].mean(), 2)
    top_industry = df['industry'].value_counts().idxmax()
    return render_template('home.html', total_jobs=total_jobs, avg_salary=avg_salary, top_industry=top_industry)


@app.route('/industry')
def industry_insights():
    top_industry = df['industry'].value_counts().idxmax()
    total_industries = df['industry'].nunique()

    highest_paid_industry = (
        df.groupby('industry')['avg_salary']
        .mean()
        .idxmax()
    )

    # Plot top 10 industries
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(y='industry', data=df, order=df['industry'].value_counts().index[:10], palette='cool')
    plt.title('Top 10 Industries Hiring AI Roles')
    plt.xlabel('Number of Jobs')
    plt.ylabel('Industry')
    img_data = fig_to_base64(fig)
    plt.close(fig)
    return render_template('industry.html',
                           img_df=img_data,
                           top_industry=top_industry,
                           total_industries=total_industries,
                           highest_paid_industry=highest_paid_industry)


@app.route('/skills')
def skills_analysis():
    from collections import Counter
    skill_series = df['skills_required'].dropna().apply(
        lambda x: [i.strip() for i in x.split(',')] if isinstance(x, str) else [])
    skill_counts = Counter([s for skills in skill_series for s in skills])
    top_skills = dict(skill_counts.most_common(10))

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=list(top_skills.values()), y=list(top_skills.keys()), palette='viridis')
    plt.title('Top 10 Most Demanded Skills')
    plt.xlabel('Number of Job Listings')
    plt.ylabel('Skill')
    img_df = fig_to_base64(fig)
    plt.close(fig)
    return render_template('skills.html', img_df=img_df)

@app.route('/experience')
def experience_insights():
    # --- Chart 1: Employment Type by Experience Level ---
    fig1, ax1 = plt.subplots(figsize=(7,5))
    sns.countplot(x='experience_level', hue='employment_type', data=df, palette='Set2', ax=ax1)
    plt.title('Employment Type Distribution by Experience Level')
    plt.xlabel('Experience Level')
    plt.ylabel('Job Count')
    plt.legend(title='Employment Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    chart1 = fig_to_base64(fig1)
    plt.close(fig1)

    # --- Chart 2: Salary Distribution by Experience Level ---
    fig2, ax2 = plt.subplots(figsize=(7,5))
    sns.boxplot(x='experience_level', y='avg_salary', data=df, palette='coolwarm', ax=ax2)
    plt.title('Salary Distribution by Experience Level')
    plt.xlabel('Experience Level')
    plt.ylabel('Average Salary (USD)')
    chart2 = fig_to_base64(fig2)
    plt.close(fig2)

    return render_template('experience.html', chart1=chart1, chart2=chart2)

def fig_to_base64(fig):
    import io, base64
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img_data

if __name__ == '__main__':
    app.run(debug=True)
