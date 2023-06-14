from django.urls import reverse
from django.test import TestCase, Client
from posts.models import Post, User, Group, Follow


class ScriptTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.not_client = Client()
        self.user = User.objects.create_user(username='leonard',
                                             password='a12345A')
        self.client.force_login(self.user)

    def testProfile(self):
        response = self.not_client.get('/leonard/')
        self.assertEqual(response.status_code, 200)

    def testNewPost(self):
        self.client.post('/new/', {'text': 'test'})
        response = self.client.get('/leonard/')
        self.assertEqual(len(response.context['page'].object_list), 1)

    def testNewPostNotLogin(self):
        response = self.not_client.post('/new/', {'text': 'test'})
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def testPost(self):
        Post.objects.create(author=self.user, text='test')
        for url in ('', '/leonard/'):
            response = self.not_client.get(url)
            self.assertEqual(len(response.context['page'].object_list), 1)
        response = self.not_client.get('/leonard/1/')
        self.assertTrue(response.context['post'])

    def testEdit(self):
        Post.objects.create(author=self.user, text='test')
        self.client.post('/leonard/1/edit/', {'text': 'newtest'})
        for url in ('', '/leonard/'):
            response = self.client.get(url)
            self.assertEqual(response.context['page'].object_list[0].text,
                             'newtest')
        response = self.client.get('/leonard/1/')
        self.assertEqual(response.context['post'].text, 'newtest')


class TemplatesTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username='leonard',
                                             password='a12345A')
        self.client.force_login(self.user)
        self.group = Group.objects.create(title='test', slug='test')
        with open('./media/posts/shot.jpeg',
                  'rb') as img:
            self.client.post('/new/',
                             {'text': 'post with image',
                              'image': img,
                              'group': self.group.id})

    def test404(self):
        response = self.client.get('/404/')
        self.assertTemplateUsed(response, 'misc/404.html')

    def testImagePost(self):
        response = self.client.get(
            reverse('post', kwargs={'username': self.user.username,
                                    'post_id': 1}))
        self.assertIn('<img', response.content.decode())

    def testImageIndex(self):
        response = self.client.get(reverse('index'))
        self.assertIn('<img', response.content.decode())

    def testImageProfile(self):
        response = self.client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertContains(response, '<img')

    def testImageGroup(self):
        response = self.client.get(reverse('group_post',
                                           kwargs={'slug': 'test'}))
        self.assertIn('<img', response.content.decode())

    def testImageSafe(self):
        with open('./media/posts/test.txt', 'rb') as img:
            self.client.post('/new/',
                             {'text': 'post with image', 'image': img})
            # self.assertRaises(ValueError)
            self.assertEqual(Post.objects.count(), 1)


class CacheTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username='leonard',
                                             password='a12345A')
        Post.objects.create(author=self.user, text='first')

    def testCache(self):
        response = self.client.get(reverse('index'))
        Post.objects.create(author=self.user, text='cache')
        self.assertNotContains(response, 'cache')


class FollowTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.not_client = Client()
        self.user = User.objects.create_user(username='leonard',
                                             password='a12345A')
        self.user_2 = User.objects.create_user(username='cohen',
                                               password='a12345A')
        self.client.force_login(self.user)

    def testFollowUnfollow(self):
        self.assertEqual(self.user.follower.count(), 0)
        self.client.get(reverse('profile_follow',
                                kwargs={'username': self.user_2.username}))
        self.assertEqual(self.user.follower.count(), 1)
        self.client.get(reverse('profile_unfollow',
                                kwargs={'username': self.user_2.username}))
        self.assertEqual(self.user.follower.count(), 0)

    def testPostForFollower(self):
        Post.objects.create(author=self.user_2, text='cache')
        self.client.get(reverse('profile_follow',
                                kwargs={'username': self.user_2.username}))
        response = self.client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page'].object_list), 1)

    def testPostForFollowing(self):
        Post.objects.create(author=self.user, text='cache')
        self.client.get(reverse('profile_follow',
                                kwargs={'username': self.user_2.username}))
        response = self.client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page'].object_list), 0)

    def testPostComment(self):
        Post.objects.create(author=self.user, text='cache')
        self.not_client.post(reverse('add_comment',
                                     kwargs={'username': 'leonard',
                                             'post_id': 1}), {'text': 'test'})
        response = self.not_client.get(reverse('post',
                                               kwargs={'username': 'leonard',
                                                       'post_id': 1}))
        self.assertNotContains(response, 'test')

    def testPostCommentLogin(self):
        Post.objects.create(author=self.user, text='cache')
        self.client.post(reverse('add_comment',
                                 kwargs={'username': 'leonard',
                                         'post_id': 1}), {'text': 'test'})
        response = self.client.get(reverse('post',
                                           kwargs={'username': 'leonard',
                                                   'post_id': 1}))
        self.assertContains(response, 'test')
