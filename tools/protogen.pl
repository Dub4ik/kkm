% This is a protocol facade mixing generator.

% Option "XkbOptions" "ctrl:nocaps,grp:sclk_toggle,grp_led:scroll,terminate:ctrl_alt_bksp"


:- dynamic([api_stream/2]).
:- discontiguous([api/1,
                  cmd/2,
                  heading/1,
                  params/2,
                  param/2,
                  param/3,
                  no_password/1,
                  command/1,
                  interprete/1,
                  postproc/1,
                  assert_cond/3,
                  rcv/4,
                  tst/4,
                  snd/4
                 ]
                ).

current_level(debug).

log_cmd(Level, Cmd, Name):-
    log_message(Cmd, Name, Msg),
    log(Level, Msg).

log_message(Cmd, Name, Message):-
    swritef(Message, 'Generated %w (%w).', [Name, Cmd]).

param(code, byte).
param(period, byte).
param(table, byte).
param(field, byte).
param(font, byte).
param(checktype, byte).
param(end, byte).
param(start, byte).
param(line_no, byte).
param(barcode, byte, 5).
param(department, byte).
param(start2, int).
param(end2, int).
param(line_no2, int).
param(repeat2, int).
param(print_flags, print_flags).
param(band_flags, band_flags).
param(graph_flags, graph_flags).
param(message40, char, 40).
param(graphics40, bytes, 40).
param(message20, char, 20).
param(port, byte).
param(parameter, byte).
param(timeout, byte).
param(name, char, 30).
param(register, register).
param(time, time).
param(date, date).
param(full, bool).
param(advert, bool).
param(value, table_value).
param(amount, bcd, 5).
param(discount_amount, bcd, 5).
param(increase_amount, bcd, 5).
param(serial, serial).
param(count, count, 5).
param(price, bcd, 5).
param(taxes, byte, 4).
param(amounts4, money, 4).
param(amounts16, money, 16).
param(data, bytes, '*').
param(data_type, bool).
param(block_no, byte).
param(data64, bytes, 64).
param(qr_type, byte).
param(data_length2, int).
param(params, bytes, 5).
param(align, byte).
param(reg_report_type, byte).
param(inn, char, 12).
param(reg_number, bytes, 20).
param(tax_code, byte).
param(work_mode, byte).
param(query_code, byte).
param(reregistration_number, byte).
param(row, int).
param(rows, byte).
param(document_number, int).
param(discount, discount_bcd, 4).
param(oper_type, byte).
param(messagez, stringz, '*').
param(reregistration_cause, byte).
param(fiscal_document_number, bytes, 4).

api(get_dump). %
cmd(get_dump, '01').
params(get_dump, [code]).
interprete(get_dump):-
    i_word('blocks_count').

api(data_dump).%
cmd(data_dump, '02').
interprete(data_dump):-
    i_byte('chip_code'),
    i_word('bolock_number'),
    rest_data.

api(data_dump_interrupt).%
cmd(data_dump_interrupt, '03').

api(get_current_state_short). %
cmd(get_current_state_short, '10'). % I.e., '\x10' in Python
interprete(get_current_state_short):-
    oper_number,
    flags,
    mode,
    submode,
    count_ops(4),
    voltage(battery),
    voltage(power_supply),
    i_error(fa),
    i_error(ecpt), % Electronic Control Protected Tape
    reserved('reserved', 3),
    % last_print_result,
    true.

api(get_current_state).
cmd(get_current_state, '11').
interprete(get_current_state):-
    oper_number, %
    soft_version('kkt_version'),
    soft_version('kkt_build'),
    date('kkt_date'),
    i_byte('number_in_room'),
    document_serial,
    flags, %
    mode, %
    submode,
    i_byte('kkt_port'),
    soft_version('fa_version'),
    soft_version('fa_build'),
    date('fa_date'),
    time('fa_time'),
    fa_flags(16),
    %% serial_no(13),
    i_data(tmp, 4),
    i_word('last_closed_session_no'),
    i_word('free_records_number'),
    i_byte('reregistration_no'),
    i_byte('rest_reregistrations'),
    inn,
    fa_mode,
    true.

document_serial:-
    i_word('document_serial').

api(print_bold). %
cmd(print_bold, '12').
params(print_bold, [print_flags, message20]).
interprete(print_bold):-
    oper_number.

api(beep). %
cmd(beep, '13').
interprete(beep):-
    oper_number.

api(set_connection). %
cmd(set_connection, '14').
params(set_connection, [P, parameter, timeout]):-
    params(get_connection, [P]).

api(get_connection). %
cmd(get_connection, '15').
params(get_connection, [port]).
interprete(get_connection):-
    i_baud(parameter),
    i_byte(timeout).

api(technological_reset). %
cmd(technological_reset, '16').

api(print). %
cmd(print, '17').
params(print, [Flags, message40]):-
    params(print_bold, [Flags, _]).
interprete(print):-
    oper_number.

api(print_header). %
cmd(print_header, '18').
params(print_header, [name, document_number]).
interprete(print_header):-
    oper_number,
    document_serial.

api(test_run). %
cmd(test_run, '19').
params(test_run, [period]).
interprete(test_run):-
    oper_number.

api(get_money_register). %
cmd(get_money_register, '1A').
params(get_money_register, [register]).
interprete(get_money_register):-
    oper_number,
    i_money_register(value).

api(get_operational_register). % But did not check register < 256
cmd(get_operational_register, '1B').
params(get_operational_register, Params):-
    params(get_money_register, Params).
interprete(get_operational_register):-
    oper_number,
    i_word(value).

api(write_table). % but value is encoded in cp1251
cmd(write_table, '1E').
params(write_table, Params):-
    params(read_table, Read),
    append(Read, [value], Params).

api(read_table). %
cmd(read_table, '1F').
params(read_table, [Number, row, field]):-
    params(query_table_structure, [Number]).
interprete(read_table):-
    rest_data(value).

api(flash_time). %
cmd(flash_time, '21').
params(flash_time, [time]).

api(flash_date). %
cmd(flash_date, '22').
params(flash_date, [date]).

api(flash_date_confirm). %
cmd(flash_date_confirm, '23').
params(flash_date_confirm, Params):-
    params(flash_date, Params).

api(init_table). %
cmd(init_table, '24').

api(cut_check). %
cmd(cut_check, '25').
params(cut_check, [full]).
interprete(cut_check):-
    oper_number.

api(font_params_read). %
cmd(font_params_read, '26').
params(font_params_read, [font]).
interprete(font_params_read):-
    i_word('print_width'),
    i_byte('width'),
    i_byte('height'),
    i_byte('count_of_fonts').

api(total_annulate). %
cmd(total_annulate, '27').

api(open_money_box). %
cmd(open_money_box, '28').
interprete(open_money_box):-
    oper_number.

api(feed). %
cmd(feed, '29').
params(feed, [band_flags, rows]).
interprete(feed):-
    oper_number.

api(cancel_test_run). %
cmd(cancel_test_run, '2B').
interprete(cancel_test_run):-
    oper_number.

api(readout_operational_registers). %
cmd(readout_operational_registers, '2C').
interprete(readout_operational_registers):-
    oper_number.

api(query_table_structure). %
cmd(query_table_structure, '2D').
params(query_table_structure, [table]).
interprete(query_table_structure):-
    i_name(name, 40),
    i_word(row_count),
    i_byte(field_count).

api(query_field_structure). %
cmd(query_field_structure, '2E').
params(query_field_structure, Params):-
    params(query_table_structure, QParams),
    append(QParams, [field], Params).
interprete(query_field_structure):-
    i_name(name, 40),
    i_bool(type),
    i_byte(length),
    rest_proc(field_vals, 'self._interp_rest_field_structure').
    %% if(type, not),
    %% i_data(min_value, length),
    %% i_data(max_value, length),
    %% endif(type).

api(print_with_font). %
cmd(print_with_font, '2F').
params(print_with_font, [print_flags, font, message40]).
interprete(print_with_font):-
    oper_number.

api(daily_report_wo_annulation). %
cmd(daily_report_wo_annulation, '40').
interprete(daily_report_wo_annulation):-
    oper_number.

api(daily_report_with_annulation). %
cmd(daily_report_with_annulation, '41').
interprete(daily_report_with_annulation):-
    oper_number.

api(section_report). %
cmd(section_report, '42').
interprete(section_report):-
    oper_number.

api(tax_report). %
cmd(tax_report, '43').
interprete(tax_report):-
    oper_number.

api(cashier_report). %
cmd(cashier_report, '44').
interprete(cashier_report):-
    oper_number.

api(deposit). %
cmd(deposit, '50').
params(deposit, [amount]).
interprete(deposit):-
    oper_number,
    document_serial.

api(withdraw).
cmd(withdraw, '51').
params(withdraw, Params):-params(deposit, Params).
interprete(withdraw):-
    oper_number,
    document_serial.

api(print_cliche). %
cmd(print_cliche, '52').
interprete(print_cliche):-
    oper_number.

api(document_finalization). %
cmd(document_finalization, '53').
params(document_finalization, [advert]).
interprete(document_finalization):-
    oper_number.

api(print_advertisement). %
cmd(print_advertisement, '54').
interprete(print_advertisement):-
    oper_number.

api(flash_serial_number). %
cmd(flash_serial_number, '60').
params(flash_serial_number, [serial]).

api(sell). %
cmd(sell, '80').
params(sell, [count, price, department, taxes, message40]).
interprete(sell):-
    oper_number.

api(buy). %
cmd(buy, '81').
params(buy, Params):-params(sell, Params).
interprete(buy):-interprete(sell).

api(cancel_sell). %
cmd(cancel_sell, '82').
params(cancel_sell, Params):-params(sell, Params).
interprete(cancel_sell):-interprete(sell).

api(cancel_buy). %
cmd(cancel_buy, '83').
params(cancel_buy, Params):-params(sell, Params).
interprete(cancel_buy):-interprete(sell).

api(cancellation). %
cmd(cancellation, '84').
params(cancellation, Params):-params(sell, Params).
interprete(cancellation):-interprete(sell).

api(close_check).
cmd(close_check, '85'). %
params(close_check, [amounts4, discount, taxes, message40]).
interprete(close_check):-
    oper_number,
    i_money(change),
    rest_data(url).

api(discount). %
cmd(discount, '86').
params(discount, [amount, taxes, message40]).
interprete(discount):-interprete(sell).

api(increse). %
cmd(increse, '87').
params(increse, Params):-params(discount, Params).
interprete(increse):-interprete(discount).

api(annulate_check). %
cmd(annulate_check, '88').
interprete(annulate_check):-interprete(cancellation).

api(subtotal). %
cmd(subtotal, '89').
interprete(subtotal):-
    oper_number,
    i_money(amount).

api(annulate_discount). %
cmd(annulate_discount, '8A').
params(annulate_discount, Params):-params(discount, Params).
interprete(annulate_discount):-interprete(discount).

api(annulate_increase). %
cmd(annulate_increase, '8B').
params(annulate_increase, Params):-params(annulate_discount, Params).
interprete(annulate_increase):-interprete(annulate_discount).

api(print_check_copy). %
cmd(print_check_copy, '8C').
interprete(print_check_copy):-
    oper_number.

api(open_check). %
cmd(open_check, '8D').
params(open_check, [checktype]).
interprete(open_check):-
    oper_number.

api(close_check_extended). %
cmd(close_check_extended, '8E').
params(close_check_extended, [amounts16 | Params]):-
    params(close_check, [amounts4 | Params]). % But number of rows is bigger.
interprete(close_check_extended):-
    interprete(close_check).

api(continue_printing). %
cmd(continue_printing, 'B0').
interprete(continue_printing):-
    oper_number.

api(load_graphics). %
cmd(load_graphics, 'C0').
params(load_graphics, [line_no, graphics40]).
interprete(load_graphics):-
    oper_number.

api(print_graphics). %
cmd(print_graphics, 'C1').
params(print_graphics, [start, end]).
interprete(print_graphics):-
    interprete(load_graphics).

api(print_ean13). %
cmd(print_ean13, 'C2').
params(print_ean13, [barcode]).
interprete(print_graphics):-
    interprete(load_graphics).

api(print_graphics_extended). %
cmd(print_graphics_extended, 'C3').
params(print_graphics_extended, [start2, end2, graph_flags]).
interprete(print_graphics_extended):-
    interprete(print_graphics).

api(load_graphics_extended). %
cmd(load_graphics_extended, 'C4').
params(load_graphics_extended, [line_no2, data]).
interprete(load_graphics_extended):-
    interprete(load_graphics).

api(print_graphics_line). %
cmd(print_graphics_line, 'C5').
params(print_graphics_line, [repeat2, graph_flags, data]).
interprete(print_graphics_line):-
    interprete(print_graphics).

api(load_data). %
cmd(load_data, 'DD').
params(load_data, [data_type, block_no, data64]).
interprete(load_data):-
    interprete(print_graphics).

api(print_qrcode). %
cmd(print_qrcode, 'DE').
params(print_qrcode, [qr_type, data_length2, start, params, align]).
interprete(print_qrcode):-
    oper_number,
    i_params(params, 5).

api(open_shift). %
cmd(open_shift, 'E0').
interprete(open_shift):-
    oper_number.

api(get_device_type). %
cmd(get_device_type, 'FC').
no_password(get_device_type).
interprete(get_device_type):-
    dev_type,
    dev_subtype,
    proto_version(proto_version),
    proto_version(proto_subversion),
    dev_model,
    dev_lang,
    rest_data(name).

api(query_fa_status). %
cmd(query_fa_status, ext('01')).
interprete(query_fa_status):-
    fa_life_status,
    document_type,
    document_data,
    shift_status,
    warning_flags,
    datetime(fa_datetime),
    fa_number,
    fd_number.

api(query_fa_number). %
cmd(query_fa_number, ext('02')).
interprete(query_fa_number):-
    fa_number.

api(query_fa_duration).%
cmd(query_fa_duration, ext('03')).
interprete(query_fa_duration):-
    date(duration).

api(query_fa_version).%
cmd(query_fa_version, ext('04')).
interprete(query_fa_version):-
    fa_version,
    soft_type.

api(begin_kkt_registration_report).%
cmd(begin_kkt_registration_report, ext('05')).
params(begin_kkt_registration_report, [reg_report_type]).

api(make_kkt_registration_report).%
cmd(make_kkt_registration_report, ext('06')).
params(make_kkt_registration_report, [inn, reg_number, tax_code, work_mode]).
interprete(make_kkt_registration_report):-
    fd_number,
    fiscal_feature.

api(reset_fa_state).
cmd(reset_fa_state, ext('07')).%
params(reset_fa_state, [query_code]).

api(cancel_fa_document).%
cmd(cancel_fa_document, ext('08')).

api(query_fiscal_results).%
cmd(query_fiscal_results, ext('09')).
params(query_fiscal_results, [reregistration_number]).
interprete(query_fiscal_results):-
    datetime(datetime),
    inn,
    kkt_reg_number,
    tax_code,
    work_mode,
    reregistration_cause,
    fd_number,
    fiscal_feature.

api(find_fd_by_nuber). %
cmd(find_fd_by_nuber, ext('0A')).
params(find_fd_by_nuber, [document_number]).
interprete(find_fd_by_nuber):-
    document_type,
    i_bool(ofd_receipt),
    rest_data(data).

api(send_TLV_struct).%
cmd(send_TLV_struct, ext('0C')).
params(send_TLV_struct, [data]).

api(discount_increase_operation). %
cmd(discount_increase_operation, ext('0D')).
params(discount_increase_operation, [oper_type, amount, price, discount_amount,
                                     increase_amount,
                                     department, taxes,
                                     barcode, messagez]).


api(make_reregistration_report).%
cmd(make_reregistration_report, ext('34')).
params(make_reregistration_report, [reregistration_cause]).
interprete(make_reregistration_report):-
    fd_number,
    fiscal_feature.

api(begin_correction_check). %
cmd(begin_correction_check, ext('35')).

api(make_correction_check). %
cmd(make_correction_check, ext('36')).
params(make_correction_check, [amount, oper_type]).
interprete(make_correction_check):-
    check_number,
    fd_number,
    fiscal_feature.

api(begin_calculation_report). %
cmd(begin_calculation_report, ext('37')).


api(make_calculation_report). %
cmd(make_calculation_report, ext('38')).
interprete(make_calculation_report):-
    fd_number,
    fiscal_feature,
    unconfirmed_count,
    date(first_unconfirmed).

api(get_info_exchange_status).%
cmd(get_info_exchange_status, ext('39')).
interprete(get_info_exchange_status):-
    i_bool(status),
    i_byte(connection),
    i_bool(reading),
    i_word(message_count),
    document_number,
    datetime(first_document).

api(query_fiscal_document_TLV). %
cmd(query_fiscal_document_TLV, ext('3A')).
params(query_fiscal_document_TLV, [fiscal_document_number]).
interprete(query_fiscal_document_TLV):-
    fiscal_type,
    i_word(length).

api(read_fiscal_document_TLV). %
cmd(read_fiscal_document_TLV, ext('3B')).
interprete(read_fiscal_document_TLV):-
    rest_data(tlv_struct).

api(query_ofd_data_transfer_receipt). %
cmd(query_ofd_data_transfer_receipt, ext('3C')).
params(query_ofd_data_transfer_receipt, [fiscal_document_number]).
interprete(query_ofd_data_transfer_receipt):-
    rest_data(receipt_data).

api(begin_fiscal_mode_closing). %
cmd(begin_fiscal_mode_closing, ext('3D')).

api(close_fiscal_mode).%
cmd(close_fiscal_mode, ext('3E')).
interprete(close_fiscal_mode):-
    fd_number,
    fiscal_feature.

api(query_fd_count_wo_receipt).%
cmd(query_fd_count_wo_receipt, ext('3F')).
interprete(query_fd_count_wo_receipt):-
    i_word(count).

api(query_current_shift_params).
cmd(query_current_shift_params, ext('40')).
interprete(query_current_shift_params):-
    shift_status,
    shift_number,
    check_number.

api(begin_shift_opening).
cmd(begin_shift_opening, ext('41')).

api(begin_shift_closing).
cmd(begin_shift_closing, ext('42')).

heading(Name):-
    write_def(Name).

close_heading:-
    writef(prog, "):\n", []).

command_const(Name, Const):-
    atom_upper(Name, Const).

constant(Name) :-
    cmd(Name, ext(Cmd)),
    command_const(Name, Const),
    writef(const, '%w = b\'\\xFF\\x%w\'\n', [Const, Cmd]).

constant(Name) :-
    cmd(Name, Cmd),
    Cmd \= ext(_),
    command_const(Name, Const),
    writef(const, '%w = b\'\\x%w\'\n', [Const, Cmd]).

atom_upper(Atom, Upper):-
    string_upper(Atom, S),
    atom_string(Upper, S).

write_def(Name):-
    api_stream(prog, S),
    writef(S, "    def %w(", [Name]).

command(Name):-
    command_const(Name, Const),
    writef(prog, '        # send command to device."""\n', []),
    writef(prog, '        self._send_command(%w, self._get_password(), bytearray(rawdata))\n', [Const]),
    writef(prog, '        # receive answer from device."""\n', []),
    writef(prog, '        answer = self._receive_answer()\n', [Const]),
    writef(prog, '        assert type(answer) in [bytes, bytearray]\n', [Const]),
    writef(prog, '        answer = bytearray(answer)\n', []),
    writef(prog, '        # Interprete the answer\n', [Const]),
    writef(prog, '        return self._interp_%w(answer)\n\n', [Name]),
    writef(prog, '    def _interp_%w(self, answer):\n', [Name]),
    check_commad_code(Name).

check_commad_code(Name):-
    cmd(Name, ext(_)), !,
    command_const(Name, Const),
    writef(prog, '        assert bytes([answer.pop(0), answer.pop(0)]) == %w, "wrong initial byte"\n', [Const]).

check_commad_code(Name):-
    command_const(Name, Const),
    writef(prog, '        assert bytes([answer.pop(0)]) == %w, "wrong initial byte"\n', [Const]).


interprete(_):-
    writef(prog, '        # This is empty interpretation body.\n\n', []).

error_check:-
    writef(prog, '        self._error_proc(answer)\n', []).

interp(Name):-
    error_check,
    writef(prog, '        rc = OrderedDict({\n', []),
    interprete(Name),
    writef(prog, '        })\n', []),
    add_assert_conds(Name),
    postproc(Name),
    writef(prog, '        rc = self._wrap("%w",rc)\n\n', [Name]),
    writef(prog, '        return rc\n\n', []).

postproc(_):-
    writef(prog, '        # A post processing rc = f(rc) \n\n', []).

add_assert_conds(Name):-
    assert_cond(Name, Condition, Description),!,
    writef(prog, '        assert %w, %w\n', [Condition, Description]),
    retract(assert_cond(Name, Condition, Description)),
    add_assert_conds(Name).

add_assert_conds(_).


% ----------- Automata -----------------------

agent(kkt).
agent(pc).

start_state(kkt, unknown).
start_state(pc,  unknown).

states(pc, [unknown, determ, wait, sstx, send,
            sent, receive, trysend, nolink,
            length, crc, checkline, check, ack,
            nak, fin, good]).

signal(stx, '02').
signal(etx, '03').
signal(eot, '04').
signal(enq, '05').
signal(ack, '06').
signal(dle, '10').
signal(nak, '15').
signal( fs, '1C').
signal( ff, 'FF').

signal0(Signal, Value):-
    signal(Signal, Value).

signal0(to, '').
signal0(other, '').

snd(pc, unknown, enq,  determ).

rcv(pc, determ,  ack,  wait).
rcv(pc, determ,  nak,  sstx).
rcv(pc, determ,  to,   nolink).

snd(pc, sstx,    stx,  send).

snd(pc, send,    data, sent).

rcv(pc, sent,    ack,  wait).
rcv(pc, sent,    other,trysend). % -> send, --i

tst(pc, trysend, true, send).
tst(pc, trysend, false,nolink).

rcv(pc, wait,    stx,  length).
rcv(pc, wait,    to,   nolink).
rcv(pc, wait,    other,nolink).

rcv(pc, length,  length,    receive).
rcv(pc, length,  to,   checkline).

rcv(pc, receive, data, crc).
rcv(pc, receive, to,   checkline).

rcv(pc, crc,     crc,  check).
rcv(pc, crc,     to,   checkline).

tst(pc, check,   true, ack).
tst(pc, check,   false,nak).

snd(pc, ack,     ack,  fin). % Response processing ?
snd(pc, nak,     nak,  checkline).

tst(pc, checkline, true, unknown).
tst(pc, checkline, false,nolink).

snd(pc, nolink,  error, nolink).

rcv(pc, fin,     ff, good).
rcv(pc, fin,     to, checkline).

snd(pc, good,    ok, good).
%rcv(pc, _,       to,  nolink). % time out


% ----------- Field interpreters -------------

oper_number:-
    i_byte('op_number', 'self._oper_number').

g_assert(Name, Condition, Description):-
    assert(assert_cond(Name, Condition, Description)).

pop_byte('answer.pop(0)').
pop_byte(Exp, Distance):-
    swritef(Exp, 'answer.pop(%w)', [Distance]).

pop_bytes('b\'\'', 0).
pop_bytes(E+bytes([P]), N):-
    N>0,
    M is N-1,
    pop_bytes(E, M),
    pop_byte(P).

pop_bytes('b\'\'', 0, _).
pop_bytes(E+bytes([P]), N, Distance):-
    N>0,
    M is N-1,
    pop_bytes(E, M, Distance),
    pop_byte(P, Distance).


skip_bytes(0, 'bytearray()').
skip_bytes(N, Exp):- N>0,
                     M is N - 1,
                     skip_bytes(M, Em),
                     pop_byte(Pop),
                     swritef(Exp, "%w + bytearray([%w])", [Em, Pop]).

pop_word(Exp) :-
    pop_byte(Lower),
    pop_byte(Higher),
    swritef(Exp, "(%w + %w << 8)", [Lower, Higher]).

i_byte(Name, Proc):-
    pop_byte(Pop),
    wr_attr(Name, Pop, Proc).

i_byte(Name):-
    pop_byte(Exp),
    wr_attr(Name, Exp).

i_word(Name):-
    pop_word(Exp),
    wr_attr(Name, Exp).

flags:-
    pop_word(Pop),
    wr_attr('flags', Pop, "KKMFlags").

check_number:-
    i_word(check_number).

mode:-
    pop_byte(Pop),
    wr_attr('mode', Pop, 'KKMMode').

submode:-
    pop_byte(Pop),
    wr_attr('submode', Pop, 'KKMSubMode').

count_ops(Distance):-
    pop_byte(Lower),
    pop_byte(Higher, Distance),
    swritef(Exp, "%w + (%w << 8)", [Lower, Higher]),
    wr_attr('count_ops', Exp).

last_print_result:-
    i_byte(last_print_result).

voltage(Name):-
    i_byte(Name).

i_error(Prefix):-
    pop_byte(Pop),
    swritef(Name, '%w_error', [Prefix]),
    swritef(Wrapper, 'self._%w_error', [Prefix]),
    wr_attr(Name, Pop, Wrapper).


soft_version(Name):-
    pop_bytes(E, 2),
    wr_attr(Name, E).


i_baud(Name):-
    i_byte(Name). % FIXME: Decoding.

data_exp(Number, Exp):-
    swritef(Exp, 'self._shift(answer, %w)', [Number]).

i_data(Name, Number):-
    data_exp(Number, Exp),
    wr_attr(Name, Exp).

fa_number:-
    i_data(fa_number, 16).

fa_version:-
    i_data(fa_version, 16).

fd_number:-
    i_data(fd_number, 4).

fiscal_feature:-
    i_data(fiscal_feature, 4).

kkt_reg_number:-
    i_data(kkt_reg_number, 20).

unconfirmed_count:-
    i_data(unconfirmed_count, 4).

document_number:-
    i_data(document_number, 4).

i_params(Name, L):-
    i_data(Name, L).

tax_code:-
    i_byte(tax_code).

work_mode:-
    i_byte(work_mode).

reregistration_cause:-
    i_byte(cause).

fiscal_type:-
    i_word(fiscal_type).

shift_number:-
    i_word(shift_number).

shift_status:-
    i_word(shift_status).


i_money(Name):- % FIXME: Check size.
    data_exp(5, Exp),
    swritef(MoneyExp, 'self._to_money(%w)', [Exp]),
    wr_attr(Name, MoneyExp).

i_money_register(Name):-
    data_exp(6, Exp),
    swritef(MoneyExp, 'self._to_money(%w)', [Exp]),
    wr_attr(Name, MoneyExp).

i_bool(Name):-
    pop_byte(B),
    wr_attr(Name, bool(B)).

soft_type:-
    i_bool(fe_release).

i_name(Name, Count):-
    i_string(Name, Count).

i_string(Name, Count):-
    data_exp(Count, Exp),
    swritef(StringExp, 'self._to_string(%w)', [Exp]),
    wr_attr(Name, StringExp).

reserved(Name, Num):-
    skip_bytes(Num, Exp),
    wr_attr(Name, Exp).

date(Name):-
    pop_byte(D),pop_byte(M),pop_byte(Y),
    wr_attr(Name, [D,M,Y]).

time(Name):-
    pop_byte(H),pop_byte(M),pop_byte(S),
    wr_attr(Name, [H,M,S]).

datetime(Name):-
    pop_byte(D),pop_byte(M),pop_byte(Y),
    pop_byte(H),pop_byte(Min),
    wr_attr(Name, [D,M,Y, H,Min]).

fa_flags(Distance):-
    pop_byte(Lower), pop_byte(Higher,Distance),
    swritef(Exp, "%w + (%w << 8)", [Lower, Higher]),
    wr_attr(fa_flags, Exp, 'FaFlags').

serial_no(Distance):-
    pop_bytes(E1, 4),
    pop_bytes(E2, 2, Distance),
    wr_attr(serial_no, E1 + E2).

inn:-
    pop_bytes(E, 6),
    wr_attr(inn, E).

fa_mode:-
    pop_byte(P),
    wr_attr(fa_mode, P).

dev_type:-
    i_byte(dev_type).

dev_subtype:-
    i_byte(dev_subtype).

proto_version(Name):-
    i_byte(Name).

proto_subversion(Name):-
    i_byte(Name).

dev_model:-
    i_byte(dev_model).

dev_lang:-
    i_byte(dev_lang).

fa_life_status:-
    i_byte(fa_life_status).

document_type:-
    i_byte(document_type).

document_data:-
    i_byte(document_data).

warning_flags:-
    i_byte(warning_flags).

rest_data(Name):-
    wr_attr(Name, 'self._shift(answer, len(answer))').

rest_data:-
    rest_data('data').

rest_proc(Name, Proc):-
    wr_attr(Name, answer, Proc).

wr_attr(Name, Exp):-
    swritef(Op, '"%w": %w', [Name, Exp]),
    writef(prog, '            %w,\n', [Op]).

wr_attr(Name, Exp, Wrapper):-
    swritef(Wr,'%w(%w)', [Wrapper, Exp]),
    wr_attr(Name, Wr).



% ----------- Generator engine ---------------

proc_params0(Name):-
    \+ params(Name, _),!,
    writef(prog, 'self', []).

proc_params0(Name):-
    params(Name, Params), !,
    writef(prog, 'self', []), !,
    param0(Params, Par, _, _),
    writef(prog, ', %w', [Par]),
    fail.

proc_params(Name):-
    proc_params0(Name).

proc_params(_).

param0(Params, X, T, M):-
    member(X, Params),
    param1(X, T, M).

param1(X, T, M):-
    param(X, T, M).

param1(X, T, no):-
    param(X, T).

conv_params(Name):-
    params(Name, Params),!,
    conv_params0(Name, Params).

conv_params(_).

conv_params0(_, Params):-
    param0(Params, Par, Type, Mult),
    conv_param(Par, Type, Mult),
    fail.

conv_params0(_,_).

conv_param(Par, Type, Mult):-
    conv_type(Par, Type, Mult, Exp), !,
    writef(prog, '        rawdata += %w\n', [Exp]).

conv_param(Par, Type, Mult):-
    writef(prog, '        # Not IMPL %w %w %w\n', [Par, Type, Mult]).

conv_type(Par, byte, no, bytes([Par])).
conv_type(Par, print_flags, no, Exp):-conv_type(Par, byte, no, Exp).
conv_type(Par, band_flags, no, Exp):-conv_type(Par, byte, no, Exp).
conv_type(Par, graph_flags, no, Exp):-conv_type(Par, byte, no, Exp).

conv_type(Par, char, N, NPar):-
    integer(N), !,
    localize(Par, NPar),
    writef(prog, '        %w = (%w+\'\\x00\'*%w)[:%w]\n', [NPar, Par, N, N]),
    writef(prog, '        %w = %w.encode(\'cp1251\')\n', [NPar, NPar]).

conv_type(Par, stringz, '*', NPar):-
    localize(Par, NPar),
    writef(prog, '        %w = (%w)[:]\n', [NPar, Par]),
    writef(prog, '        %w = %w.encode(\'cp1251\')+b\'\\x00\'\n', [NPar, NPar]).

conv_type(Par, bytes, N, NPar):-
    integer(N), N>=0,
    swritef(NPar, '(%w)[:%w]', [Par, N]).

conv_type(Par, bytes, '*', bytes(Par)).

conv_type(Par, utfchar, N, NPar):-
    integer(N), !,
    localize(Par, NPar),
    writef(prog, '        %w = %w[:%w]\n', [NPar, Par, N]),
    writef(prog, '        %w = %w.encode(\'utf8\')\n', [NPar, NPar]).

conv_type(Par, int, no, NPar):-
    swritef(NPar, '(%w).to_bytes(2, sys.byteorder)', [Par]).

conv_type(Par, register, no, NPar):-
    localize(Par, NPar),
    writef(prog, '        if %w<256: %w = bytes([%w])\n', [Par, NPar, Par]),
    writef(prog, '        else: %w = (%w).to_bytes(2, sys.byteorder)\n',
           [NPar, Par]).

conv_type(Par, table_value, no, Exp):-
    conv_type(Par, char, 40, Exp).

conv_type(Par, time, no, bytes(list(Par))).
conv_type(Par, date, no, Exp):-conv_type(Par, time, no, Exp).
conv_type(Par, bool, no, bytes([int(Par)])).
conv_type(Par, bcd, N, Exp):-
    integer(N),!,
    swritef(Exp, 'self._amount_to_bytes(%w, width=5, pos=2)', [Par]).

conv_type(Par, count, N, Exp):-
    integer(N),!,
    swritef(Exp, 'self._amount_to_bytes(%w, width=5, pos=3)', [Par]).

conv_type(Par, discount_bcd, N, Exp):-
    integer(N),!,
    swritef(Exp, 'self._amount_to_bytes(%w, width=2, pos=2)', [Par]).

conv_type(Par, serial, no, Exp):-
    swritef(Exp, 'self._serial_to_bytes(%w)', [Par]).

conv_type(_, byte, 0, 'b\'\'').
conv_type(Par, byte, N, bytes(Par)):-
    N>0.

conv_type(_, money, 0, 'b\'\'').
conv_type(Par, money, N, Exp + NPar):-
    N>0,
    M is N - 1,
    conv_type(Par, money, M, Exp),
    swritef(Par1,'%w[%w]', [Par, M]),
    conv_type(Par1, bcd, 5, NPar).

localize(Par, LPar):-
    swritef(LPar, '_%w', [Par]).

gen_api(Name):-
    constant(Name),!,
    heading(Name), !,
    proc_params(Name), !,
    close_heading, !,
    writef(prog, '        rawdata = b\'\'\n', []),
    conv_params(Name), !,
    command(Name), !,
    interp(Name), !,
    cmdmap(Name), !,
    true.


cmdmap(Name):-
    command_const(Name, Const),
    writef(prog, '    CMDMAP[%w]=_interp_%w\n\n', [Const, Name]).

gen_state(Dev, Name):-
    state_method(Dev, Name, Method),!,
    writef(prog, '\n    def %w(self):\n', [Method]),!,
    state_snd(Dev, Name),
    state_rcv(Dev, Name),
    state_tst(Dev, Name).

state_method(Dev, Name, Method):-
    swritef(Method, 'state_%w_%w', [Dev, Name]).

next_state(_, Name, Name, _):-!.
next_state(Dev, _, Next, Shift):-
    state_method(Dev, Next, Method),
    add_shift(Shift, String),
    writef(prog, '        %wreturn self.%w\n', [String, Method]), !.

add_shift(0, ""):-!.
add_shift(N, String):- N > 0,
    M is N - 1,
    add_shift(M, S),
    swritef(String, '    %w', [S]).

next_state(Dev, Name, Next):-
    next_state(Dev, Name, Next, 0).

state_snd(Dev, Name):-
    snd(Dev, Name, Signal, Next),
    signal(Signal, Byte),
    !, % Only one signal could be sent
    writef(prog, '        self._send_char(b\'\\x%w\')\n', [Byte]), !,
    next_state(Dev, Name, Next).

state_snd(Dev, Name):-
    snd(Dev, Name, data, Next), !,
    writef(prog, '        self._send_data(self.data)\n', []),
    next_state(Dev, Name, Next).

state_snd(Dev, Name):-
    snd(Dev, Name, error, Next), !,
    writef(prog, '        self._error(\'%w\')\n', [Name]),
    next_state(Dev, Name, Next).

state_snd(Dev, Name):-
    snd(Dev, Name, ok, Next), !,
    writef(prog, '        self._good(\'%w\')\n', [Name]),
    next_state(Dev, Name, Next).

state_snd(_, _).

state_rcv_interp(Dev, Name, Next):-
    rcv(Dev, Name, data, Next), !,
    writef(prog, '        self.data = self._recv_data(self.size)\n', []).

state_rcv_interp(Dev, Name, Next):-
    rcv(Dev, Name, length, Next), !,
    writef(prog, '        self.size = self._recv_byte()\n', []).

state_rcv_interp(Dev, Name, Next):-
    rcv(Dev, Name, crc, Next), !,
    writef(prog, '        self.crc = self._recv_char()\n', []),
    writef(prog, '        self.crc_calculated = self._calculate_crc()\n', []).

state_rcv_interp(Dev, Name, Name):-
    rcv(Dev, Name, Signal, _),
    signal0(Signal, _), !,
    writef(prog, '        ch = self._recv_char()\n', []),
    state_rcv_signal(Dev, Name).

state_rcv(Dev, Name):-
    state_rcv_interp(Dev, Name, Next),
    next_state(Dev, Name, Next).

state_rcv(_, _).

state_rcv_signal(Dev, Name):-
    rcv(Dev, Name, Signal, Next),
    signal(Signal, Byte),
    writef(prog, '        if ch == b\'\\x%w\':\n', [Byte]),
    next_state(Dev, Name, Next, 1),
    fail.

state_rcv_signal(Dev, Name):-
    rcv(Dev, Name, to, Next),
    writef(prog, '        if ch == \'\':\n', []),
    next_state(Dev, Name, Next, 1),
    fail.

state_rcv_signal(Dev, Name):-
    rcv(Dev, Name, other, Next),
    writef(prog, '        if len(ch)>0:\n', []),
    next_state(Dev, Name, Next, 1),
    fail.
state_rcv_signal(_, _):-
    writef(prog, '        else:\n', []),
    writef(prog, '            raise RuntimeError("wrong char")\n', []).


state_tst(Dev, Name):-
    tst(Dev, Name, What, Next),
    state_tst_interp(Dev, Name, What, Next),
    fail.

state_tst(Dev, Name):-
    tst(Dev, Name, _, _),!,
    writef(prog, '        # Testing %w-%w\n', [Dev, Name]), !.

state_tst(_, _).

test_attempt(trysend, send_tries).
test_attempt(checkline, recv_tries).

state_tst_interp(Dev, Name, true, Next):-
    test_attempt(Name, TriesName),
    writef(prog, '        self.%w-=1\n', [TriesName]),
    writef(prog, '        if self.%w >= 0:\n', [TriesName]),
    next_state(Dev, Name, Next, 1).

state_tst_interp(Dev, Name, false, Next):-
    test_attempt(Name, TriesName),
    writef(prog, '        if self.%w <= 0:\n', [TriesName]),
    next_state(Dev, Name, Next, 1).

state_tst_interp(Dev, check, true, Next):-
    writef(prog, '        if self.crc == self.calculated_crc:\n', []),
    next_state(Dev, check, Next, 1).

state_tst_interp(Dev, check, false, Next):-
    writef(prog, '        if self.crc != self.calculated_crc:\n', []),
    next_state(Dev, check, Next, 1).

state_header:-
    writef(prog, '\nclass StateMachine(BaseStateMachine):\n',[]),
    writef(prog, '    """Definition of the protocol state machine"""\n',[]).

generate :-
    api(Name),
    log(info, 'Generating %w.', [Name]),
    gen_api(Name),
    fail.

generate :-
    state_header,
    state(Dev, State),
    log(info, 'Generating State %w  %w.', [State, Dev]),
    gen_state(Dev, State),
    fail.

generate.

state(Dev, X):-states(Dev, L), member(X, L).

run :- gen, halt.

gen :-
    remove_loggers,
    retractall(api_stream(_)),
    setup_api_streams,
    setup_logging,
    log(info, '------ Started new run ------'),
    generate,!.

setup_logging:-
    setup_logger(console),
    setup_logger(file, "Generated.log", append).

api_file(prog, 'api.py',[
             'from .commands import *',
             'from .base import BaseApi, BaseStateMachine',
             'from .base import *',
             'from collections import OrderedDict',
             'import sys',
             '',
             '',
             'class Api(BaseApi):',
             '    """Api implementation mixin."""',
             '',
             '    CMDMAP={}'
                        ]).
api_file(const, 'commands.py',[]).

setup_api_streams:-
    api_file(Type, FileName, Operators),
    swritef(PathName, "../kkm/driver/fa01/%w", [FileName]),
    open(PathName, write, Api),
    write_preamble(Api),
    write_operators(Api, Operators),
    assert(api_stream(Type, Api)),
    fail.

setup_api_streams.

write_preamble(Api):-
    write(Api, "#!/usr/bin/env python\n"),
    write(Api, "# encoding:utf-8\n"),
    write(Api, "# This file is generated, do not edit it.\n\n").

write_operators(_, []):-!.
write_operators(S, [X|T]):-
    write(S, X),
    write(S, '\n'),
    write_operators(S, T).

% ------------ Service procedures -----------------

writef(Atom, Message, Arguments):-
    atom(Atom),!,
    api_stream(Atom, Stream),
    writef(Stream, Message, Arguments).

writef(Stream, Message, Arguments):-
    swritef(S, Message, Arguments),
    write(Stream, S).

:- dynamic([logger_driver/1]).

level(none,0).
level(critical,10).
level(error,20).
level(info,30).
level(debug,40).
level(trace,50).


setup_logger(console):-
    current_stream(1, write, S),
    assert(logger_driver(S)).

setup_logger(file, FileName):-
    open(FileName, write, Out),
    assert(logger_driver(Out)).

setup_logger(file, FileName, append):-
    open(FileName, append, Out),
    assert(logger_driver(Out)).

log(Level, Message):-
    current_level(L),
    level(L, Y),
    level(Level, X),
    X=<Y,!,
    string_upper(Level, LEVEL),
    swritef(S, '%w:%w\n', [LEVEL, Message]),
    write_log_line(S),!.

log(_, _).

log(Level, Message, Vars):-
    swritef(Msg, Message, Vars),
    log(Level, Msg).

write_log_line(L):-
    logger_driver(Logger),
    write(Logger, L), fail.

write_log_line(_).

remove_loggers:-
    retractall(logger_driver(_)),!.

remove_loggers.

% :- remove_loggers.
% :- gen.
