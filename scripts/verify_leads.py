from core.database import SessionLocal, Lead
import pandas as pd

def list_leads():
    db = SessionLocal()
    leads = db.query(Lead).all()
    db.close()
    
    if not leads:
        print("📭 No leads found in the database.")
        return
    
    data = []
    for lead in leads:
        data.append({
            "Platform": lead.platform,
            "Title": lead.title,
            "Budget": lead.budget,
            "URL": lead.url,
            "Status": lead.status,
            "Date": lead.created_at.strftime("%Y-%m-%d %H:%M")
        })
    
    df = pd.DataFrame(data)
    print(df.to_string(index=False))

if __name__ == "__main__":
    list_leads()
