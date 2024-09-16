from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Technology

# SQLite database file path for products
DATABASE_URI = 'sqlite:///products.db'

# Create engine for products database
engine = create_engine(DATABASE_URI)

# Create all tables for products database
Base.metadata.create_all(engine)

# Add items to the products database
Session = sessionmaker(bind=engine)
session = Session()

# Populate technologies
technologies = [
    { 'name': "Creatine Monohydrate", 'price': 6, 'description': "Creatine is a natural compound that boosts energy in muscles, aiding high-intensity activities. Widely used in sports supplements for enhanced strength and muscle growth.", 'image': "creatine.jpeg", 'carbon': 5.2},
    { 'name': "Pure Whey Protein", 'price': 12,'description': "High-quality milk-derived protein for muscle building and recovery.", 'image': "whey-protein.jpeg", 'carbon': 8.83 },
    { 'name': "Electrolyte Powder", 'price': 5, 'description': "Electrolyte powder is a convenient and efficient way to replenish essential minerals lost through sweat during physical activity. Packed with sodium, potassium, magnesium, and calcium, this powder helps maintain proper hydration, supports muscle function, and aids in preventing cramps and fatigue.", 'image': "electrolyte-powder.jpeg", 'carbon': 4.1},
    { 'name': "Pre-workout", 'price': 7, 'description': "Elevate your workouts with our premium pre-workout blend! Packed with energy-boosting ingredients like caffeine and beta-alanine, it's the perfect fuel to maximize your performance and crush your fitness goals.", 'image': "Pre-workout.jpeg", 'carbon': 7.5},
    { 'name': "Omega-3 Fish Oil", 'price': 15, 'description': "Omega-3 fatty acids are essential nutrients that are important for maintaining heart health, brain function, and overall wellness. Fish oil supplements provide a convenient source of omega-3s, particularly EPA (eicosapentaenoic acid) and DHA (docosahexaenoic acid).", 'image': "omega-3-fish-oil.jpeg", 'carbon': 9.8},
    { 'name': "Multivitamin Tablets", 'price': 8, 'description': "Multivitamin tablets contain a combination of essential vitamins and minerals that are important for overall health and well-being. They can help fill nutrient gaps in your diet and support various bodily functions, including immune function, energy production, and bone health.", 'image': "multivitamin-tablets.jpeg", 'carbon': 3.6},
    { 'name': "Plant-Based Protein Powder", 'price': 18, 'description': "Plant-based protein powder is made from sources such as peas, brown rice, hemp, and quinoa. It provides a vegan-friendly alternative to animal-based protein powders and is rich in essential amino acids, making it suitable for muscle building and recovery.", 'image': "plant-based-protein-powder.jpeg", 'carbon': 5.1},
    { 'name': "Iron Supplements", 'price': 11, 'description': "Iron supplements provide a source of this essential mineral, vital for the production of hemoglobin and red blood cells. They help prevent iron deficiency anemia and support overall energy levels, cognitive function, and immune health.", 'image': "iron-supplements.jpeg", 'carbon': 6.1},
]

for tech_data in technologies:
    existing_tech = session.query(Technology).filter_by(name=tech_data['name']).first()
    if existing_tech is None:
        session.add(Technology(**tech_data))

# Committing changes to the products database
session.commit()
