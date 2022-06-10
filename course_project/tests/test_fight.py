from app.database import User, create_session
from app.fight import attack, attack_b, fight


class TestFight:
    def test_fight(self, default_user1):
        with create_session() as session:
            user1 = default_user1
            user2 = User(
                login='User2',
                guild='%_no_guild_%',
                money=1000,
                food=0,
                rank='member',
                rating=0,
                password='123',
                buildings_power=500,
                army_power=20,
                all_power=520,
                HQ_level=1,
                Miner1_level=1,
                Miner2_level=1,
                Wh_level=1,
                turret_level=1,
                soldiers_t1=10,
                soldiers_t2=0,
                soldiers_t3=0,
                soldiers_t4=0,
                soldiers_t5=0,
            )
            user3 = User(
                login='User3',
                guild='%_no_guild_%',
                money=0,
                food=0,
                rank='member',
                rating=0,
                password='123',
                buildings_power=500,
                army_power=2000,
                all_power=2500,
                HQ_level=1,
                Miner1_level=1,
                Miner2_level=1,
                Wh_level=1,
                turret_level=1,
                soldiers_t1=1000,
                soldiers_t2=0,
                soldiers_t3=0,
                soldiers_t4=0,
                soldiers_t5=0,
            )
            user4 = User(
                login='User4',
                guild='%_no_guild_%',
                money=0,
                food=0,
                rank='member',
                rating=0,
                password='123',
                buildings_power=500,
                army_power=2100,
                all_power=2100,
                HQ_level=1,
                Miner1_level=1,
                Miner2_level=1,
                Wh_level=1,
                turret_level=1,
                soldiers_t1=1050,
                soldiers_t2=0,
                soldiers_t3=0,
                soldiers_t4=0,
                soldiers_t5=0,
            )
            session.add(user1)
            session.add(user2)
            session.add(user3)
            session.add(user4)
            assert fight(user1, user2) == {'rating': '-10', 'result': 'lost'}
            assert fight(user3, user1) == {
                'food': 0,
                'money': 0,
                'rating': '+10',
                'result': 'won',
            }
            assert fight(user4, user3) == {'rating': '+1', 'result': 'draw'}

    def test_attack(self, default_user1):
        # 1 - сам себя, 2 - не существует, 3 - рейтинг, 4 - одна гильдия, 5 - бой
        assert attack('attacks himself', 'attacks himself') == {
            'error': 'you cannot attack yourself!'
        }
        assert attack('player1', 'player2') == {'error': 'no user found'}

        with create_session() as session:
            user1 = default_user1
            user2 = User(
                login='User2',
                guild='%_no_guild_%',
                money=1000,
                food=0,
                rank='member',
                rating=500,
                password='123',
                buildings_power=500,
                army_power=20,
                all_power=520,
                HQ_level=1,
                Miner1_level=1,
                Miner2_level=1,
                Wh_level=1,
                turret_level=1,
                soldiers_t1=10,
                soldiers_t2=0,
                soldiers_t3=0,
                soldiers_t4=0,
                soldiers_t5=0,
            )
            session.add(user1)
            session.add(user2)
            session.commit()
            assert attack(user1.login, user2.login) == {
                'error': 'difference between ratings is too big (>100)'
            }
            user1.guild = 'guild'
            user2.guild = 'guild'
            user2.rating = 0
            user1.login = 'User3'
            user2.login = 'User4'
            session.add(user1)
            session.add(user2)
            session.commit()
            assert attack(user1.login, user2.login) == {
                'error': 'you cannot attack a player from your guild!'
            }
            user1.guild = 'lala'
            user1.login = 'User5'
            session.add(user1)
            session.commit()
            assert attack(user1.login, user2.login) == {
                'result': 'lost',
                'rating': '-10',
            }

    def test_attacl_b(self, default_user1):
        with create_session() as session:
            user1 = default_user1
            session.add(user1)
            session.commit()
            assert attack_b(user1.login, 5) == {'result': 'lost', 'rating': '-10'}
