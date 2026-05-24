#!/usr/bin/env python3
"""Quick sanity check before restarting backend"""

import sys
import os

# Set backend path
backend_path = r"c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\backend"
os.chdir(backend_path)
sys.path.insert(0, backend_path)

print(f"CWD: {os.getcwd()}")

# Test imports
try:
    from config.db import build_engine, Base
    print("✓ config.db imported")
    
    from model.dataStructure import Bateria, Prueba
    print("✓ model.dataStructure imported")
    
    from services.bateria import create_bateria
    print("✓ services.bateria imported")
    
    from services.prueba import create_prueba_with_bateria_aux
    print("✓ services.prueba imported")
    
    # Test engine build
    engine = build_engine()
    print("✓ Engine built")
    
    Base.metadata.create_all(engine)
    print("✓ Tables created")
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    db = Session()
    print("✓ Session created")
    
    # Quick test of normalization
    from serializers.prueba import PruebaCreateAux
    prueba_data = PruebaCreateAux(
        num_buses=2, 
        num_stations=4, 
        max_stops=3,
        num_stops=[3, 2],
        st_bi=[[1, 0, 1, 0], [0, 1, 0, 1]],
        d=[[0, 14, 18, 22], [14, 0, 11, 19]],
        t=[[0, 9, 12, 16], [9, 0, 10, 13]],
        tau_bi=[[6, 18, 30, 42], [8, 20, 32, 44]],
        consumo_max=100,
        consumo_min=20,
        alpha=1.5,
        mu=8.0,
        sm=3,
        psi=2.5,
        beta=12.0,
        m=1000,
    )
    print(f"✓ Pydantic model created: {prueba_data}")
    
    # Test normalization
    normalized = prueba_data.model_dump(exclude_none=True)
    print(f"✓ Normalized (exclude_none=True): {len(normalized)} fields")
    
    db.close()
    print("\n✅ All sanity checks passed!")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
