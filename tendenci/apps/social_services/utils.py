def get_responder_skills_data(skillset):

    # Emergency Response Skills
    emergency_skills = [skillset.filter(paramedic=True).count(),
                        skillset.filter(fireman=True).count(),
                        skillset.filter(first_aid=True).count(),
                        skillset.filter(safety_manager=True).count(),
                        skillset.filter(police=True).count(),
                        skillset.filter(search_and_rescue=True).count(),
                        skillset.filter(scuba_certified=True).count(),
                        skillset.filter(crowd_control=True).count()]
    # Transportation Skills
    transportation_skills = [skillset.filter(truck=True).count(),
                             skillset.filter(pilot=True).count(),
                             skillset.filter(ship=True).count(),
                             skillset.filter(sailor=True).count()]
    # Medical Skills
    medical_skills = [skillset.filter(doctor=True).count(),
                      skillset.filter(nurse=True).count()]
    # Communication Skills
    communication_skills = [skillset.filter(crisis_communication=True).count(),
                            skillset.filter(media=True).count(),
                            skillset.filter(author=True).count(),
                            skillset.filter(public_speaker=True).count(),
                            skillset.filter(politician=True).count(),
                            skillset.filter(blogger=True).count(),
                            skillset.filter(photographer=True).count(),
                            skillset.filter(videographer=True).count(),
                            skillset.filter(radio_operator=True).count(),
                            skillset.filter(actor=True).count(),
                            skillset.filter(thought_leader=True).count(),
                            skillset.filter(influencer=True).count()]
    # Education Skills
    education_skills = [skillset.filter(teacher=True).count(),
                        skillset.filter(school_admin=True).count()]
    # Military Skills
    military_skills = [skillset.filter(military_training=True).count(),
                       skillset.filter(desert_trained=True).count(),
                       skillset.filter(cold_trained=True).count(),
                       skillset.filter(marksman=True).count()]

    return [emergency_skills, transportation_skills, medical_skills,
            communication_skills, education_skills, military_skills]
