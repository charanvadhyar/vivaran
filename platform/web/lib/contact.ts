import { many, one } from "./db";
import { GRIEVANCE_ACK_HOURS, GRIEVANCE_RESOLVE_DAYS, ticket as ticketOf, type Kind } from "./contactKinds";

export { GRIEVANCE_ACK_HOURS, GRIEVANCE_RESOLVE_DAYS, KINDS, MESSAGES_PER_NETWORK_PER_DAY, isKind, ticket, type Kind } from "./contactKinds";

export type NewMessage = {
  kind: Kind; topic: string | null; name: string; email: string; organisation: string | null; phone: string | null;
  message: string; aboutUrl: string | null; userId: string | null; network: string | null;
};

export async function sentToday(network: string): Promise<number> {
  const row = await one<{ n: number }>(
    `select count(*)::int as n from contact_messages where network = $1 and created_at > now() - interval '24 hours'`, [network]);
  return Number(row?.n ?? 0);
}

export async function save(m: NewMessage): Promise<string> {
  const row = await one<{ id: string }>(
    `insert into contact_messages (kind, topic, name, email, organisation, phone, message, about_url, user_id, network)
     values ($1, $2, $3, $4, $5, $6, $7, $8, $9::uuid, $10) returning id::text`,
    [m.kind, m.topic, m.name, m.email, m.organisation, m.phone, m.message, m.aboutUrl, m.userId, m.network]);
  return ticketOf(row!.id);
}

export type Message = {
  id: string; kind: Kind; topic: string | null; name: string; email: string; organisation: string | null; phone: string | null;
  message: string; about_url: string | null; handle: string | null; status: "new" | "acknowledged" | "resolved" | "closed";
  admin_note: string | null; created_at: Date; acknowledged_at: Date | null; resolved_at: Date | null; age_hours: number;
};

/** Messages for the admin page: open ones first, oldest first; or the latest of all. */
export function messages(show: "open" | "all", kind: Kind | null) {
  return many<Message>(`
    select m.id::text, m.kind, m.topic, m.name, m.email, m.organisation, m.phone, m.message, m.about_url, u.handle,
           m.status, m.admin_note, m.created_at, m.acknowledged_at, m.resolved_at,
           extract(epoch from now() - m.created_at)::float / 3600 as age_hours
      from contact_messages m left join users u on u.id = m.user_id
     where ($1 = 'all' or m.status in ('new', 'acknowledged')) and ($2::text is null or m.kind = $2)
     order by extract(epoch from m.created_at) * case when $1 = 'all' then -1 else 1 end
     limit 200`, [show, kind]);
}

export async function counts() {
  return one<{ open: number; grievances_open: number; grievances_late: number; unanswered: number }>(`
    select count(*) filter (where status in ('new', 'acknowledged'))::int as open,
           count(*) filter (where kind = 'grievance' and status in ('new', 'acknowledged'))::int as grievances_open,
           count(*) filter (where kind = 'grievance' and status in ('new', 'acknowledged')
                            and created_at < now() - make_interval(days => ${GRIEVANCE_RESOLVE_DAYS}))::int as grievances_late,
           count(*) filter (where status = 'new' and created_at < now() - make_interval(hours => ${GRIEVANCE_ACK_HOURS}))::int as unanswered
      from contact_messages`);
}

export async function update(id: string, status: Message["status"], note: string | null) {
  await one(`
    update contact_messages set status = $2, admin_note = $3,
      acknowledged_at = case when $2 <> 'new' then coalesce(acknowledged_at, now()) else acknowledged_at end,
      resolved_at = case when $2 in ('resolved', 'closed') then coalesce(resolved_at, now()) else null end
     where id = $1::bigint returning id`, [id, status, note]);
}
