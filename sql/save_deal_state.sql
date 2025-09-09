create or replace function save_deal_state()
returns trigger as $$
begin
    if tg_op = 'UPDATE' then
        if (old.sale_stage_id is distinct from new.sale_stage_id) or
        (old.probability is distinct from new.probability) or
        (old.lost_reason_id is distinct from new.lost_reason_id) or
        (old.lost_reason_additional_text is distinct from new.lost_reason_additional_text) or
        (old.manager_id is distinct from new.manager_id)
        then
            insert into deal_history
            (
                deal_id, sale_stage_id,
                probability, lost_reason_id,
                manager_id, lost_reason_additional_text,
                changed_at
            )
            values
            (
                old.deal_id, old.sale_stage_id,
                old.probability, old.lost_reason_id,
                old.manager_id, old.lost_reason_additional_text,
                current_timestamp
            );
        end if;
        return new;

    elsif tg_op = 'DELETE' then
        insert into deal_history
        (
            deal_id, sale_stage_id,
            probability, lost_reason_id,
            manager_id, lost_reason_additional_text,
            changed_at
        )
        values
        (
            old.deal_id, old.sale_stage_id,
            old.probability, old.lost_reason_id,
            old.manager_id, old.lost_reason_additional_text,
            current_timestamp
        );
        return old;
    end if;
    return new;
end;
$$ language plpgsql;


create trigger trigger_save_deal_state_version
before update or delete on deal
for each row execute function save_deal_state();
