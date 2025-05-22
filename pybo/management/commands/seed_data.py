import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files import File
from pybo.models import Question, Answer, Comment

class Command(BaseCommand):
    help = 'Seed database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            default=5,
            type=int,
            help='Number of users to create'
        )
        parser.add_argument(
            '--questions',
            default=20,
            type=int,
            help='Number of questions to create'
        )
        parser.add_argument(
            '--answers',
            default=3,
            type=int,
            help='Max number of answers per question'
        )
        parser.add_argument(
            '--comments',
            default=5,
            type=int,
            help='Max number of comments per question/answer'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_questions = options['questions']
        max_answers = options['answers']
        max_comments = options['comments']

        self.stdout.write(self.style.SUCCESS(f'Creating {num_users} users...'))
        users = self._create_users(num_users)

        self.stdout.write(self.style.SUCCESS(f'Creating {num_questions} questions...'))
        questions = self._create_questions(users, num_questions)

        self.stdout.write(self.style.SUCCESS(f'Creating answers...'))
        answers = self._create_answers(users, questions, max_answers)

        self.stdout.write(self.style.SUCCESS(f'Creating comments...'))
        self._create_comments(users, questions, answers, max_comments)

        self.stdout.write(self.style.SUCCESS(f'Creating votes...'))
        self._create_votes(users, questions, answers)

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def _create_users(self, num_users):
        users = []
        # Always create a superuser or get it if it exists
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'Superuser created: {admin.username}')
        else:
            self.stdout.write(f'Using existing superuser: {admin.username}')
        users.append(admin)

        # Create regular users or get them if they exist
        for i in range(1, num_users + 1):
            username = f'user{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'user{i}@example.com'
                }
            )
            if created:
                user.set_password(f'password{i}')
                user.save()
                self.stdout.write(f'User created: {user.username}')
            else:
                self.stdout.write(f'Using existing user: {user.username}')
            users.append(user)

        return users

    def _create_questions(self, users, num_questions):
        questions = []
        image_files = self._get_image_files()

        # Sample question subjects and content
        subjects = [
            "Django 프로젝트에서 모델 관계 설정하기",
            "파이썬 가상환경 설정 방법",
            "JavaScript와 Python 비교",
            "데이터베이스 정규화란?",
            "REST API 설계 원칙",
            "웹 개발에서 보안 고려사항",
            "프론트엔드 프레임워크 비교",
            "백엔드 개발자가 알아야 할 것들",
            "클라우드 서비스 활용하기",
            "CI/CD 파이프라인 구축",
            "마이크로서비스 아키텍처",
            "컨테이너화와 도커",
            "머신러닝 기초 개념",
            "데이터 시각화 도구",
            "성능 최적화 전략",
            "버전 관리 시스템 Git",
            "테스트 주도 개발(TDD)",
            "애자일 방법론",
            "프로젝트 관리 도구",
            "코드 리뷰 방법",
            "오픈 소스 기여하기",
            "프로그래밍 언어 트렌드",
            "알고리즘과 자료구조",
            "디자인 패턴",
            "리팩토링 기법",
            "코딩 스타일 가이드",
            "API 문서화",
            "서버리스 아키텍처",
            "블록체인 기술",
            "인공지능 윤리"
        ]

        contents = [
            "이 주제에 대해 자세히 알고 싶습니다. 경험이 있으신 분들의 조언 부탁드립니다.",
            "최근에 이 기술을 사용해보려고 하는데 어떻게 시작해야 할지 모르겠습니다.",
            "이 개념에 대한 좋은 학습 자료나 튜토리얼을 추천해주세요.",
            "실무에서 이 기술을 어떻게 활용하고 계신가요? 장단점이 궁금합니다.",
            "이 기술의 최신 트렌드는 무엇인가요? 앞으로의 발전 방향이 궁금합니다.",
            "초보자가 이해하기 쉽게 설명해주실 수 있나요?",
            "이 기술을 사용할 때 주의해야 할 점은 무엇인가요?",
            "실제 프로젝트에서 이 기술을 적용한 사례를 공유해주세요.",
            "이 기술의 대안으로는 어떤 것들이 있나요?",
            "이 기술을 배우는 데 얼마나 시간이 걸릴까요?",
            "이 기술이 미래에도 계속 중요할까요?",
            "이 기술을 사용하면서 겪은 문제와 해결 방법을 알려주세요.",
            "이 기술을 효율적으로 사용하는 팁이 있을까요?",
            "이 기술을 배우기 위한 로드맵을 제안해주세요.",
            "이 기술을 사용하는 회사나 프로젝트를 알려주세요."
        ]

        # Create questions
        for i in range(num_questions):
            # Select a random user as the author
            author = random.choice(users)

            # Select a random subject and content
            subject = random.choice(subjects)
            content = random.choice(contents)

            # Create a random date within the last 30 days
            days_ago = random.randint(0, 30)
            create_date = timezone.now() - timedelta(days=days_ago)

            # Decide if this question has an image (70% chance)
            has_image = random.random() < 0.7

            # Create the question
            question = Question(
                author=author,
                subject=f"{subject} #{i+1}",
                content=f"{content}\n\n이 질문은 테스트 데이터입니다. #{i+1}",
                create_date=create_date
            )

            # Add an image if needed
            if has_image and image_files:
                image_path = random.choice(image_files)
                with open(image_path, 'rb') as img_file:
                    file_name = os.path.basename(image_path)
                    question.image.save(file_name, File(img_file), save=False)

            question.save()
            questions.append(question)
            self.stdout.write(f'Question created: {question.subject}')

            # Add some random modification dates (30% chance)
            if random.random() < 0.3:
                days_after_creation = random.randint(0, min(5, days_ago))
                modify_date = create_date + timedelta(days=days_after_creation)
                question.modify_date = modify_date
                question.save()

        return questions

    def _create_answers(self, users, questions, max_answers):
        answers = []

        # Sample answer contents
        answer_contents = [
            "제 경험에 따르면, 이 문제는 다음과 같이 해결할 수 있습니다.",
            "이 주제에 대해 좋은 자료를 찾았습니다. 다음 링크를 참고하세요: https://example.com",
            "비슷한 상황을 겪었는데, 다음 방법으로 해결했습니다.",
            "이 문제는 생각보다 복잡할 수 있습니다. 다음 사항을 고려해보세요.",
            "간단한 해결책은 없지만, 다음 단계를 따라하면 도움이 될 것입니다.",
            "제가 추천하는 방법은 다음과 같습니다.",
            "이 문제에 대한 공식 문서를 확인해보세요. 매우 유용한 정보가 있습니다.",
            "저도 처음에는 어려웠지만, 다음 방법으로 배웠습니다.",
            "이 문제는 다양한 관점에서 접근할 수 있습니다. 제 의견은 다음과 같습니다.",
            "실무에서는 보통 다음과 같이 처리합니다.",
            "이론적으로는 여러 방법이 있지만, 실제로는 다음 방법이 가장 효율적입니다.",
            "최신 트렌드를 고려하면, 다음 접근 방식이 좋을 것 같습니다.",
            "이 문제는 다음 단계로 나누어 생각해볼 수 있습니다.",
            "제 경험상 가장 중요한 것은 다음 원칙을 지키는 것입니다.",
            "초보자라면 다음 순서로 배우는 것이 좋습니다."
        ]

        # Create answers for each question
        for question in questions:
            # Determine number of answers for this question (0 to max_answers)
            num_answers = random.randint(0, max_answers)

            for j in range(num_answers):
                # Select a random user as the author (not the question author)
                available_users = [user for user in users if user != question.author]
                if not available_users:
                    available_users = users

                author = random.choice(available_users)

                # Select a random content
                content = random.choice(answer_contents)

                # Create a random date after the question creation date
                question_date = question.create_date
                days_after_question = random.randint(0, 30 - (timezone.now() - question_date).days)
                create_date = question_date + timedelta(days=days_after_question)
                if create_date > timezone.now():
                    create_date = timezone.now()

                # Create the answer
                answer = Answer(
                    author=author,
                    question=question,
                    content=f"{content}\n\n이 답변은 테스트 데이터입니다. #{j+1}",
                    create_date=create_date
                )

                answer.save()
                answers.append(answer)
                self.stdout.write(f'Answer created for question: {question.subject}')

                # Add some random modification dates (20% chance)
                if random.random() < 0.2:
                    days_after_creation = random.randint(0, min(3, (timezone.now() - create_date).days))
                    modify_date = create_date + timedelta(days=days_after_creation)
                    if modify_date > timezone.now():
                        modify_date = timezone.now()
                    answer.modify_date = modify_date
                    answer.save()

        return answers

    def _create_comments(self, users, questions, answers, max_comments):
        # Sample comment contents
        comment_contents = [
            "좋은 정보 감사합니다!",
            "이 내용이 많은 도움이 되었습니다.",
            "추가 질문이 있습니다. 더 자세히 설명해주실 수 있나요?",
            "다른 관점에서 생각해볼 필요가 있을 것 같습니다.",
            "이 방법을 시도해봤는데 잘 작동했습니다.",
            "참고할 만한 자료를 더 추천해주실 수 있나요?",
            "이 내용에 동의합니다. 제 경험도 비슷했습니다.",
            "흥미로운 접근 방식이네요. 더 알아보고 싶습니다.",
            "이 문제에 대한 다른 해결책도 있을까요?",
            "명확한 설명 감사합니다.",
            "이 내용을 실제로 적용해봤는데 효과적이었습니다.",
            "좋은 질문이네요. 저도 배우고 있습니다.",
            "이 주제에 대한 최신 정보를 공유해주셔서 감사합니다.",
            "이 방법의 장단점을 더 설명해주실 수 있나요?",
            "매우 유용한 팁입니다. 감사합니다!"
        ]

        # Create comments for questions
        for question in questions:
            # Determine number of comments for this question (0 to max_comments)
            num_comments = random.randint(0, max_comments)

            for j in range(num_comments):
                # Select a random user as the author
                author = random.choice(users)

                # Select a random content
                content = random.choice(comment_contents)

                # Create a random date after the question creation date
                question_date = question.create_date
                days_after_question = random.randint(0, 30 - (timezone.now() - question_date).days)
                create_date = question_date + timedelta(days=days_after_question)
                if create_date > timezone.now():
                    create_date = timezone.now()

                # Create the comment
                comment = Comment(
                    author=author,
                    content=f"{content} (테스트 댓글 #{j+1})",
                    create_date=create_date,
                    question=question
                )

                comment.save()
                self.stdout.write(f'Comment created for question: {question.subject}')

                # Add some random modification dates (10% chance)
                if random.random() < 0.1:
                    days_after_creation = random.randint(0, min(2, (timezone.now() - create_date).days))
                    modify_date = create_date + timedelta(days=days_after_creation)
                    if modify_date > timezone.now():
                        modify_date = timezone.now()
                    comment.modify_date = modify_date
                    comment.save()

        # Create comments for answers
        for answer in answers:
            # Determine number of comments for this answer (0 to max_comments)
            num_comments = random.randint(0, max_comments)

            for j in range(num_comments):
                # Select a random user as the author
                author = random.choice(users)

                # Select a random content
                content = random.choice(comment_contents)

                # Create a random date after the answer creation date
                answer_date = answer.create_date
                days_after_answer = random.randint(0, 30 - (timezone.now() - answer_date).days)
                create_date = answer_date + timedelta(days=days_after_answer)
                if create_date > timezone.now():
                    create_date = timezone.now()

                # Create the comment
                comment = Comment(
                    author=author,
                    content=f"{content} (테스트 댓글 #{j+1})",
                    create_date=create_date,
                    answer=answer
                )

                comment.save()
                self.stdout.write(f'Comment created for answer to question: {answer.question.subject}')

                # Add some random modification dates (10% chance)
                if random.random() < 0.1:
                    days_after_creation = random.randint(0, min(2, (timezone.now() - create_date).days))
                    modify_date = create_date + timedelta(days=days_after_creation)
                    if modify_date > timezone.now():
                        modify_date = timezone.now()
                    comment.modify_date = modify_date
                    comment.save()

    def _create_votes(self, users, questions, answers):
        # Add votes to questions (each user has 40% chance to vote on each question)
        for question in questions:
            for user in users:
                # Skip if user is the author (can't vote on own question)
                if user == question.author:
                    continue

                # 40% chance to vote
                if random.random() < 0.4:
                    question.voter.add(user)
                    self.stdout.write(f'Vote added to question: {question.subject}')

        # Add votes to answers (each user has 30% chance to vote on each answer)
        for answer in answers:
            for user in users:
                # Skip if user is the author (can't vote on own answer)
                if user == answer.author:
                    continue

                # 30% chance to vote
                if random.random() < 0.3:
                    answer.voter.add(user)
                    self.stdout.write(f'Vote added to answer for question: {answer.question.subject}')

    def _get_image_files(self):
        # Get all image files from the test_image directory
        image_dir = os.path.join(os.getcwd(), 'test_image')
        if not os.path.exists(image_dir):
            self.stdout.write(self.style.WARNING(f'Image directory not found: {image_dir}'))
            return []

        image_files = []
        for file_name in os.listdir(image_dir):
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_files.append(os.path.join(image_dir, file_name))

        self.stdout.write(f'Found {len(image_files)} image files')
        return image_files
