insert into memeviewer_memetemplate (name, bg_color, add_date, accepted, friendly_name, image_file, bg_image_file, change_date, meme_count)
select name, bg_color, add_date, accepted, friendly_name, image_file, bg_image_file, change_date, 0
from lb_templates
where not exists (select 1 from memeviewer_memetemplate where name = lb_templates.name);

insert into memeviewer_memetemplateslot (id, x, y, w, h, rotate, blur, grayscale, cover, template_id, slot_order)
select id, x, y, w, h, rotate, blur, grayscale, cover, template_id, slot_order
from lb_template_slots
where not exists (select 1 from memeviewer_memetemplateslot where id = lb_template_slots.id);

insert into memeviewer_memetemplate_contexts (id, memetemplate_id, memecontext_id)
select id, memetemplate_id, memecontext_id
from lb_template_contexts
where not exists (select 1 from memeviewer_memetemplate_contexts where id = lb_template_contexts.id)
