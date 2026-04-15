from fastapi import APIRouter, HTTPException, Depends
from database import db
from config import PLAN_LIMITS
from auth_utils import get_current_user

router = APIRouter(tags=["analytics"])


@router.get("/dashboard/stats")
async def get_dashboard_stats(user=Depends(get_current_user)):
    chatbot_count = await db.chatbots.count_documents({'user_id': user['user_id']})
    sub = await db.subscriptions.find_one({'user_id': user['user_id']}, {'_id': 0})
    messages_used = sub.get('messages_used_this_month', 0) if sub else 0
    plan = user.get('plan', 'free')
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])

    return {
        'total_chatbots': chatbot_count,
        'messages_this_month': messages_used,
        'message_limit': limits['messages'],
        'chatbot_limit': limits['chatbots'],
        'plan': plan,
        'active_sessions': 0,
    }


@router.get("/analytics")
async def get_analytics(user=Depends(get_current_user)):
    plan = user.get('plan', 'free')
    if plan not in ('pro', 'agency'):
        raise HTTPException(status_code=403, detail="Analytics requires Pro plan or higher")

    chatbots = await db.chatbots.find({'user_id': user['user_id']}, {'_id': 0}).to_list(100)
    chatbot_ids = [c['chatbot_id'] for c in chatbots]

    messages = await db.messages.find({'chatbot_id': {'$in': chatbot_ids}}, {'_id': 0}).to_list(10000)

    daily_counts = {}
    for msg in messages:
        if msg.get('role') == 'user':
            day = msg.get('created_at', '')[:10]
            if day:
                daily_counts[day] = daily_counts.get(day, 0) + 1

    question_counts = {}
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '').strip()
            if content and content != '[deleted]':
                key = content[:100]
                question_counts[key] = question_counts.get(key, 0) + 1
    top_questions = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    german_words = {'der', 'die', 'das', 'und', 'ist', 'ich', 'ein', 'eine', 'von', 'für', 'mit', 'auf', 'nicht', 'den', 'wir', 'sie', 'sind', 'hat', 'wie', 'bitte', 'danke', 'hallo', 'guten'}
    english_words = {'the', 'and', 'is', 'are', 'was', 'for', 'with', 'not', 'you', 'this', 'that', 'have', 'from', 'they', 'been', 'what', 'how', 'when', 'where', 'hello', 'please', 'thank'}
    french_words = {'le', 'la', 'les', 'des', 'est', 'une', 'que', 'pour', 'dans', 'pas', 'qui', 'sur', 'avec', 'tout', 'bonjour', 'merci'}
    spanish_words = {'el', 'la', 'los', 'las', 'del', 'una', 'por', 'con', 'para', 'que', 'hola', 'gracias'}

    language_counts = {}
    for msg in messages:
        if msg.get('role') == 'user':
            content = msg.get('content', '').lower()
            words = set(content.split())
            de_score = len(words & german_words)
            en_score = len(words & english_words)
            fr_score = len(words & french_words)
            es_score = len(words & spanish_words)
            scores = {'Deutsch': de_score, 'English': en_score, 'Français': fr_score, 'Español': es_score}
            best = max(scores, key=scores.get)
            if scores[best] > 0:
                language_counts[best] = language_counts.get(best, 0) + 1
            else:
                language_counts['Deutsch'] = language_counts.get('Deutsch', 0) + 1

    hour_counts = {}
    for msg in messages:
        if msg.get('role') == 'user':
            created = msg.get('created_at', '')
            if len(created) >= 13:
                try:
                    hour = int(created[11:13])
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                except ValueError:
                    pass
    peak_hours = [{'hour': h, 'count': hour_counts.get(h, 0)} for h in range(24)]

    chatbot_stats = []
    for bot in chatbots:
        bot_msgs = [m for m in messages if m.get('chatbot_id') == bot['chatbot_id']]
        chatbot_stats.append({
            'chatbot_id': bot['chatbot_id'],
            'business_name': bot.get('business_name', ''),
            'total_messages': len(bot_msgs),
            'user_messages': len([m for m in bot_msgs if m.get('role') == 'user']),
        })

    return {
        'messages_per_day': [{'date': k, 'count': v} for k, v in sorted(daily_counts.items())],
        'total_messages': len(messages),
        'total_chatbots': len(chatbots),
        'top_questions': [{'question': q, 'count': c} for q, c in top_questions],
        'language_distribution': [{'language': k, 'count': v} for k, v in sorted(language_counts.items(), key=lambda x: x[1], reverse=True)],
        'peak_hours': peak_hours,
        'chatbot_stats': chatbot_stats,
    }
