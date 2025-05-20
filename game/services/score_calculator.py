from django.apps import apps

def calculate_scores_for_game(game):
    Question = apps.get_model('game', 'Question')
    UserLocation = apps.get_model('game', 'UserLocation')
    UserScore = apps.get_model('game', 'UserScore')

    scores = list(UserScore.objects.filter(game=game))

    perf_list = []
    for score in scores:
        locs = UserLocation.objects.filter(game=game, user=score.user)
        total_dist_m = sum((loc.distance or 0) for loc in locs)
        dist_km = total_dist_m / 1000.0

        if score.end_date_time:
            hours = (score.end_date_time - game.start_date_time).total_seconds() / 3600.0
            raw_p = dist_km / hours if hours > 0 else 0
        else:
            raw_p = 0

        perf_list.append((score, raw_p))

    perf_list.sort(key=lambda x: x[1], reverse=True)
    n = len(perf_list)
    if n == 0:
        return

    for idx, (score, raw_p) in enumerate(perf_list):
        correct_qs = Question.objects.filter(
            game=game, user=score.user, is_correct=True
        )
        ques_score = sum(q.ques_dif_level * 5 for q in correct_qs)

        all_qs = Question.objects.filter(game=game, user=score.user)
        bonus  = sum(q.answer_time * (q.ques_dif_level / 10) for q in all_qs)

        if score.end_date_time:
            spent_min   = (score.end_date_time - game.start_date_time).total_seconds() / 60.0
            allowed_min = game.time / 60.0
            time_score  = max(allowed_min - spent_min, 0) + bonus
        else:
            time_score = 0

        loc_score = round((n - idx) * (100.0 / n))

        total_score = ques_score + time_score + loc_score

        score.ques_score     = ques_score
        score.time_score     = time_score
        score.location_score = loc_score
        score.total_score    = total_score
        score.save(update_fields=[
            'ques_score', 'time_score',
            'location_score', 'total_score'
        ])