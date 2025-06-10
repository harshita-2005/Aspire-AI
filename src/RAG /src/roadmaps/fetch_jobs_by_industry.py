from dotenv import load_dotenv
import os
from pinecone import Pinecone
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "rag"
# Storing Job Data in Pinecone (Metadata + Embeddings)
pinecone_index = pc.Index(index_name)
def search_job_roles_by_industry(industry):
    """Fetches job roles available in a specific industry from Pinecone."""

    try:
        # ✅ Preserve case (Do not convert to lowercase)
        industry = industry.strip()  

        # ✅ Query Pinecone with exact case-sensitive match
        results = pinecone_index.query(
            vector=[0]*1024,  # Dummy vector to fetch all jobs in the industry
            top_k=100,  # Fetch up to 100 job roles
            include_metadata=True,
            filter={"sub_industry": {"$eq": industry}}  # ✅ Case-sensitive match
        )

        # ✅ Extract unique job roles
        job_roles = set()
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            job_roles.add(metadata.get("title", "Unknown Job Role"))

        return sorted(job_roles) if job_roles else ["No job roles found"]

    except Exception as e:
        print(f"❌ Error fetching job roles for industry {industry}: {e}")
        return []
