from .models import OemPart, Problem, db


def seed_if_empty():
    if Problem.query.count() > 0:
        return

    demo_items = [
        Problem(
            title='Misfire under hard acceleration',
            model='S60 Polestar',
            engine='2.0 T6 Drive-E',
            model_year='2017',
            category='Engine',
            symptoms='Hesitation at high load, rough pull in upper RPM, and occasional check engine light after aggressive driving.',
            likely_cause='Ignition coil fatigue, worn spark plugs, or fueling inconsistency under heavy load.',
            recommended_fix='Scan for codes, inspect plugs and coils, verify service history, and test with known good premium fuel.',
            severity='high',
            author_name='Seed Admin',
            source_note='Starter entry for demo database.',
        ),
        Problem(
            title='Harsh front suspension knock on broken roads',
            model='V60 Polestar',
            engine='2.0 T6 Drive-E',
            model_year='2017',
            category='Suspension',
            symptoms='Sharp impact or clunking sound from the front over potholes or rough city streets.',
            likely_cause='Possible wear in top mounts, sway bar links, dampers, or front bushings.',
            recommended_fix='Inspect front suspension parts, compare cold and warm behavior, and rule out wheel/tire damage.',
            severity='medium',
            author_name='Seed Admin',
            source_note='Starter entry for demo database.',
        ),
        Problem(
            title='City fuel consumption feels abnormally high',
            model='S60 Polestar',
            engine='2.0 T6 Drive-E',
            model_year='2017',
            category='Fuel',
            symptoms='Very high average consumption in short-trip urban driving with frequent cold starts.',
            likely_cause='Traffic profile, cold engine operation, tire pressure, driving style, or maintenance state rather than a hard fault.',
            recommended_fix='Track several full tanks, verify tire pressure, check filters and plugs, and compare route patterns before replacing parts.',
            severity='low',
            author_name='Seed Admin',
            source_note='Starter entry for demo database.',
        ),
        Problem(
            title='Haldex AWD engagement feels delayed',
            model='S60 Polestar',
            engine='3.0 T6',
            model_year='2015',
            category='Drivetrain',
            symptoms='Rear axle feels slow to engage under slippery launch or hard throttle from low speed.',
            likely_cause='Aged Haldex fluid, clogged pump screen, or software/adaptation issues.',
            recommended_fix='Inspect and service the Haldex system, confirm maintenance record, and scan drivetrain faults.',
            severity='high',
            author_name='Seed Admin',
            source_note='Starter entry for demo database.',
        ),
        Problem(
            title='Brake fade after repeated hard driving',
            model='V60 Polestar',
            engine='3.0 T6',
            model_year='2016',
            category='Brakes',
            symptoms='Pedal gets longer and braking confidence drops after repeated high-speed stops.',
            likely_cause='Heat-soaked pads and fluid on spirited road use or track-style driving.',
            recommended_fix='Inspect pad condition, fluid age, rotor condition, and move to better fluid/pad setup if usage demands it.',
            severity='high',
            author_name='Seed Admin',
            source_note='Starter entry for demo database.',
        ),
    ]

    for item in demo_items:
        item.ensure_slug()
        db.session.add(item)

    db.session.commit()

    # ── OEM parts seed data ──────────────────────────────────────────────
    if OemPart.query.count() == 0:
        from .ai_verify import verify_oem_part

        demo_parts = [
            {
                'part_number': '31316107',
                'part_name': 'Polestar performance optimisation',
                'description': 'ECU software upgrade that increases engine output and improves throttle response for the 2.0 T6 Drive-E engine.',
                'model': 'S60 Polestar',
                'category': 'ECU',
                'author_name': 'Seed Admin',
            },
            {
                'part_number': '31470471',
                'part_name': 'Front strut brace',
                'description': 'Polestar-branded front strut tower brace for improved chassis rigidity and sharper turn-in.',
                'model': 'V60 Polestar',
                'category': 'Suspension',
                'author_name': 'Seed Admin',
            },
            {
                'part_number': '31408876',
                'part_name': 'Rear brake pad set',
                'description': 'Genuine Volvo OEM rear brake pads for Polestar models with the upgraded Brembo brake package.',
                'model': 'S60 Polestar',
                'category': 'Brakes',
                'author_name': 'Seed Admin',
            },
        ]

        for data in demo_parts:
            result = verify_oem_part(
                data['part_number'], data['part_name'],
                data['description'], data['model'], data['category'],
            )
            part = OemPart(
                part_number=data['part_number'],
                part_name=data['part_name'],
                description=data['description'],
                model=data['model'],
                category=data['category'],
                author_name=data['author_name'],
                ai_verified=result['verified'],
                ai_verdict=result['verdict'],
            )
            part.ensure_slug()
            db.session.add(part)

        db.session.commit()
