from tendenci.apps.stories.models import Story


def copy_story(story, user):

    new_story = Story.objects.create(
        title=story.title,
        content=story.content,
        syndicate=story.syndicate,
        full_story_link=story.full_story_link,
        link_title=story.link_title,
        start_dt=story.start_dt,
        end_dt=story.end_dt,
        expires=story.expires,
        image=story.image,
        group=story.group,
        tags=story.tags,
        allow_anonymous_view=story.allow_anonymous_view,
        allow_user_view=story.allow_user_view,
        allow_member_view=story.allow_member_view,
        allow_user_edit=story.allow_user_edit,
        allow_member_edit=story.allow_member_edit,
        creator=user,
        creator_username=user.username,
        owner=user,
        owner_username=user.username,
        status=story.status,
        status_detail=story.status_detail,
    )

    return new_story
