from app import app, db
from models import Item, Stock
import json

def initialize_database():
    """Initialize the database with preset uniform data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if items already exist
        if Item.query.count() > 0:
            print("Database already contains items. Skipping initialization.")
            return
        
        # Sample data structure based on your existing frontend data
        uniform_data = {
            'preschool': {
                'pe_tshirt': {
                    'name': 'PE T-shirt',
                    'sizes': {
                        '6': 240, '8': 240, '10': 240, '12': 240, '14': 240,
                        '16': 255, '18': 255, '20': 255, 'XS': 255, 'S': 270
                    }
                },
                'pe_pants': {
                    'name': 'PE Jogging Pants',
                    'sizes': {
                        '6': 380, '8': 380, '10': 380, '12': 380, '14': 380,
                        '16': 380, '18': 380, '20': 380
                    }
                },
                'male': {
                    'polo_shirt': {
                        'name': 'Polo Shirt',
                        'sizes': {
                            '6': 350, '8': 350, '10': 350, '12': 350, '14': 350,
                            '16': 350, '18': 350, '20': 350
                        }
                    },
                    'short_pants': {
                        'name': 'Short Pants',
                        'sizes': {
                            '6': 360, '8': 360, '10': 360, '12': 360, '14': 360,
                            '16': 360, '18': 360, '20': 360
                        }
                    }
                },
                'female': {
                    'blouse': {
                        'name': 'Blouse',
                        'sizes': {
                            '6': 370, '8': 370, '10': 370, '12': 370, '14': 370,
                            '16': 370, '18': 370, '20': 370
                        }
                    },
                    'skirt': {
                        'name': 'Skirt',
                        'sizes': {
                            '6': 360, '8': 360, '10': 360, '12': 360, '14': 360,
                            '16': 360, '18': 360, '20': 360
                        }
                    },
                    'patch': {
                        'name': 'Patch',
                        'sizes': {
                            'Regular': 120
                        }
                    }
                }
            },
            'elementary': {
                'pe_tshirt': {
                    'name': 'PE T-shirt',
                    'sizes': {
                        'S': 255, 'M': 255, 'L': 255, 'XL': 270, '2XL': 270,
                        '3XL': 270
                    }
                },
                'pe_pants': {
                    'name': 'PE Jogging Pants',
                    'sizes': {
                        'S': 380, 'M': 380, 'L': 380, 'XL': 380, '2XL': 380,
                        '3XL': 380
                    }
                },
                'male': {
                    'polo_shirt': {
                        'name': 'Polo Shirt',
                        'sizes': {
                            'S': 350, 'M': 350, 'L': 350, 'XL': 350, '2XL': 350,
                            '3XL': 350
                        }
                    },
                    'pants': {
                        'name': 'Pants',
                        'sizes': {
                            'S': 360, 'M': 360, 'L': 360, 'XL': 360, '2XL': 360,
                            '3XL': 360
                        }
                    }
                },
                'female': {
                    'blouse': {
                        'name': 'Blouse',
                        'sizes': {
                            'S': 370, 'M': 370, 'L': 370, 'XL': 370, '2XL': 370,
                            '3XL': 370
                        }
                    },
                    'skirt': {
                        'name': 'Skirt',
                        'sizes': {
                            'S': 360, 'M': 360, 'L': 360, 'XL': 360, '2XL': 370,
                            '3XL': 370
                        }
                    },
                    'patch': {
                        'name': 'Patch',
                        'sizes': {
                            'Regular': 120
                        }
                    }
                }
            },
            'juniorhigh': {
                'pe_tshirt': {
                    'name': 'PE T-shirt',
                    'sizes': {
                        'XS': 250, 'S': 250, 'M': 260, 'L': 260, 'XL': 270,
                        '2XL': 270, '3XL': 280
                    }
                },
                'pe_pants': {
                    'name': 'PE Jogging Pants',
                    'sizes': {
                        'S': 450, 'M': 450, 'L': 460, 'XL': 480, '2XL': 480,
                        '3XL': 500
                    }
                },
                'male': {
                    'polo_shirt': {
                        'name': 'Polo Shirt w/ Patch',
                        'sizes': {
                            'XS': 375, 'S': 390, 'M': 400, 'L': 415, 'XL': 440,
                            '2XL': 460, '3XL': 490, '4XL': 520
                        }
                    },
                    'pants': {
                        'name': 'Pants',
                        'sizes': {
                            '22': 265, 'XS': 265, 'S': 275, 'M': 285, 'L': 295,
                            'XL': 305, '2XL': 315, '3XL': 335
                        }
                    }
                },
                'female': {
                    'blouse': {
                        'name': 'Blouse w/ Patch',
                        'sizes': {
                            'XS': 295, 'S': 295, 'M': 295, 'L': 295, 'XL': 325,
                            '2XL': 325, '3XL': 385, '4XL': 345
                        }
                    },
                    'skirt': {
                        'name': 'Skirt',
                        'sizes': {
                            'S': 365, 'M': 365, 'L': 365, 'XL': 385, '2XL': 385,
                            '3XL': 430, '4XL': 435, '5XL': 460
                        }
                    },
                    'patch': {
                        'name': 'Patch',
                        'sizes': {
                            'Regular': 120
                        }
                    },
                    'necktie': {
                        'name': 'Necktie',
                        'sizes': {
                            'Regular': 180
                        }
                    }
                }
            },
            'seniorhigh': {
                'pe_tshirt': {
                    'name': 'PE T-shirt',
                    'sizes': {
                        'XS': 280, 'S': 280, 'M': 280, 'L': 290, 'XL': 290,
                        '2XL': 310, '3XL': 330
                    }
                },
                'pe_pants': {
                    'name': 'PE Jogging Pants',
                    'sizes': {
                        'S': 450, 'M': 450, 'L': 460, 'XL': 480, '2XL': 480,
                        '3XL': 500
                    }
                },
                'male': {
                    'polo_shirt': {
                        'name': 'Polo Shirt',
                        'sizes': {
                            'XS': 360, 'S': 360, 'M': 375, 'L': 375, 'XL': 425,
                            '2XL': 425, '3XL': 475, '4XL': 505, '5XL': 515
                        }
                    },
                    'pants': {
                        'name': 'Pants',
                        'sizes': {
                            '22': 285, 'XS': 285, 'S': 310, 'M': 335, 'L': 345,
                            'XL': 360, '2XL': 370, '3XL': 380, '4XL': 405
                        }
                    }
                },
                'female': {
                    'blouse': {
                        'name': 'Blouse',
                        'sizes': {
                            'XS': 360, 'S': 360, 'M': 375, 'L': 375, 'XL': 425,
                            '2XL': 425, '3XL': 475, '4XL': 545
                        }
                    },
                    'skirt': {
                        'name': 'Skirt',
                        'sizes': {
                            'S': 365, 'M': 365, 'L': 365, 'XL': 365, '2XL': 385,
                            '3XL': 370, '4XL': 435, '5XL': 390
                        }
                    },
                    'patch': {
                        'name': 'Patch',
                        'sizes': {
                            'Regular': 120
                        }
                    },
                    'necktie': {
                        'name': 'Necktie',
                        'sizes': {
                            'Regular': 180
                        }
                    },
                    'pin': {
                        'name': 'Pin',
                        'sizes': {
                            'Regular': 100
                        }
                    }
                }
            }
        }
        
        # Add items to database
        for category, category_data in uniform_data.items():
            # Handle PE items which are gender-neutral
            if 'pe_tshirt' in category_data:
                # Add PE T-shirt item
                pe_tshirt = Item(
                    name=category_data['pe_tshirt']['name'],
                    category=category,
                    gender='unisex',
                    item_type='pe_tshirt'
                )
                db.session.add(pe_tshirt)
                db.session.flush()  # Get ID before adding stocks
                
                # Add PE T-shirt stocks
                for size, price in category_data['pe_tshirt']['sizes'].items():
                    stock = Stock(
                        item_id=pe_tshirt.id,
                        size=size,
                        quantity=10,  # Default starting quantity
                        price=price,
                        threshold=3   # Default low stock threshold
                    )
                    db.session.add(stock)
            
            if 'pe_pants' in category_data:
                # Add PE Pants item
                pe_pants = Item(
                    name=category_data['pe_pants']['name'],
                    category=category,
                    gender='unisex',
                    item_type='pe_pants'
                )
                db.session.add(pe_pants)
                db.session.flush()  # Get ID before adding stocks
                
                # Add PE Pants stocks
                for size, price in category_data['pe_pants']['sizes'].items():
                    stock = Stock(
                        item_id=pe_pants.id,
                        size=size,
                        quantity=10,  # Default starting quantity
                        price=price,
                        threshold=3   # Default low stock threshold
                    )
                    db.session.add(stock)
            
            # Handle gender-specific items
            for gender in ['male', 'female']:
                if gender in category_data:
                    for item_type, item_data in category_data[gender].items():
                        # Add item
                        item = Item(
                            name=item_data['name'],
                            category=category,
                            gender=gender,
                            item_type=item_type
                        )
                        db.session.add(item)
                        db.session.flush()  # Get ID before adding stocks
                        
                        # Add stocks
                        for size, price in item_data['sizes'].items():
                            stock = Stock(
                                item_id=item.id,
                                size=size,
                                quantity=10,  # Default starting quantity
                                price=price,
                                threshold=3   # Default low stock threshold
                            )
                            db.session.add(stock)
        
        db.session.commit()
        print("Database initialized successfully with uniform data!")

if __name__ == "__main__":
    with app.app_context():
        initialize_database() 