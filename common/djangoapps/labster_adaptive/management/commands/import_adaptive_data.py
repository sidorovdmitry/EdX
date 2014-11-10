import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from labster_adaptive.models import Scale, Station, Problem, Answer


"""
Item Number,Type,Number of Destractors,Question,Content,Responses,Difficulty,FeedBack text,Scales,Station,Time (sek.),SD Time,Discrimination,Guessing
https://s3-us-west-2.amazonaws.com/labster/adaptive/item_bank.csv
"""

class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('item_bank.csv', 'rb') as csv_file:
            reader = csv.reader(csv_file)
            for each in list(reader)[1:]:

                item_number = each[0]
                answer_type = each[1]
                number_of_destractors = each[2]
                question = each[3]
                content = each[4]
                responses = each[5]
                difficulties = each[6]
                feedback = each[7]
                scales = each[8]
                stations = each[9]
                problem_time = each[10]
                sd_time = each[11]
                discrimination = each[12]
                guessing = each[13]

                response_list = responses.split(';')
                difficulty_list = difficulties.split(';')

                try:
                    problem = Problem.objects.get(item_number=item_number)
                except:
                    problem = Problem(item_number=item_number)

                problem.answer_type = answer_type
                problem.number_of_destractors = number_of_destractors
                problem.question = question
                problem.content = content
                problem.feedback = feedback
                problem.time = problem_time
                problem.sd_time = sd_time
                problem.discrimination = discrimination
                problem.guessing = guessing
                problem.modified_at = timezone.now()
                problem.save()

                for scale in scales.split(','):
                    scale = scale.strip()
                    try:
                        scale_obj = Scale.objects.get(id=scale)
                    except Scale.DoesNotExist:
                        scale_obj = Scale.objects.create(id=scale, name=scale)

                    problem.scales.add(scale_obj)

                for station in stations.split(','):
                    station = station.strip()
                    try:
                        station_obj = Station.objects.get(id=station)
                    except Station.DoesNotExist:
                        station_obj = Station.objects.create(id=station, name=station)

                    problem.stations.add(station_obj)

                Answer.objects.filter(problem=problem).update(is_active=False)
                for index, response in enumerate(response_list):
                    difficulty = None
                    if len(response_list) == len(difficulty_list):
                        difficulty = difficulty_list[index]

                    try:
                        answer = Answer.objects.get(
                            problem=problem,
                            answer=response,
                        )
                    except Answer.DoesNotExist:
                        answer = Answer(
                            problem=problem,
                            answer=response,
                        )

                    answer.is_correct = index == 0
                    answer.difficulty = difficulty
                    answer.is_active = True
                    answer.save()
