import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from services.mapping_service import MappingService
from schemas import TranslateRequest, FHIRParameter

async def test_demo_translation():
    """Test the translation that the demo should be calling"""
    
    try:
        # Create the request object like the frontend does
        request = TranslateRequest(
            resourceType='Parameters',
            parameter=[
                FHIRParameter(name='system', valueUri='http://ayush.namaste.gov.in/ayurveda'),
                FHIRParameter(name='code', valueCode='AYU-SH-3.13'),
                FHIRParameter(name='target', valueUri='http://id.who.int/icd/entity')
            ]
        )
        
        # Get database session and call mapping service
        async for db in get_db_session():
            mapping_service = MappingService()
            response = await mapping_service.translate_concept(db, request)
            
            print("✅ Translation successful!")
            print(f"Result: {response.result}")
            print(f"Message: {response.message}")
            
            if response.match:
                for i, match in enumerate(response.match):
                    print(f"\nMatch {i+1}:")
                    print(f"  NAMASTE Code: {match.namasteCode}")
                    print(f"  NAMASTE Term: {match.namasteTerm}")
                    print(f"  ICD-11 Code: {match.icd11Code}")
                    print(f"  ICD-11 Term: {match.icd11Term}")
                    print(f"  Equivalence: {match.equivalence}")
                    print(f"  Confidence: {match.confidence}")
                    print(f"  Clinical Notes: {match.clinicalNotes[:100]}...")
            else:
                print("No matches found")
            
            break
            
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    print("Testing demo translation for AYU-SH-3.13...")
    success = asyncio.run(test_demo_translation())
    if success:
        print("\n🎉 Demo translation test PASSED!")
    else:
        print("\n💥 Demo translation test FAILED!")