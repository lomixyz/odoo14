$(document).ready(function (e) {
    $.ajax({
        url: "/user-group",
        data: {},
        type: "post",
        cache: false,
        success: function (result) {
            var datas = JSON.parse(result);
            if (datas.user == "1") {
                $("#leader_div").addClass("o_hidden");
                $("#team_div").addClass("o_hidden");
                $("#assign_user_div").addClass("o_hidden");
            } else if (datas.leader == "1") {
                $("#leader_div").addClass("o_hidden");
            } else if (datas.manager == "1") {
                $("#leader_div").removeClass("o_hidden");
                $("#team_div").removeClass("o_hidden");
                $("#assign_user_div").removeClass("o_hidden");
            }
        },
    });
    var filter_date = $("#days_filter").children("option:selected").val();
    if (filter_date == "custom") {
        $("#start_date").removeClass("o_hidden");
        $("#end_date").removeClass("o_hidden");
    } else {
        $("#start_date").addClass("o_hidden");
        $("#end_date").addClass("o_hidden");
        $("#start_date").val("");
        $("#end_date").val("");
    }
    $.get(
        "/get-ticket-table-data",
        {
            team: $("#team").val(),
            team_leader: $("#team_leader").val(),
            user_id: $("#assign_user").val(),
            filter_date: $("#days_filter").children("option:selected").val(),
            date_start: $("#start_date").val(),
            date_end: $("#end_date").val(),
        },
        function (result) {
            $("#js_ticket_tbl_div").replaceWith(result);
        }
    );
    $.get(
        "/get-ticket-counter-data",
        {
            team: $("#team").val(),
            team_leader: $("#team_leader").val(),
            user_id: $("#assign_user").val(),
            filter_date: $("#days_filter").children("option:selected").val(),
            date_start: $("#start_date").val(),
            date_end: $("#end_date").val(),
        },
        function (result) {
            $("#js_ticket_count_div").replaceWith(result);
        }
    );
    $.get("/get_team", function (data) {
        obj = JSON.parse(data);

        for (var key in obj) {
            $("#team").append('<option value="' + key + '" >' + obj[key].name + "</option>");
        }
    });
    $.get("/get_team_leader", function (data) {
        obj = JSON.parse(data);

        for (var key in obj) {
            $("#team_leader").append('<option value="' + key + '" >' + obj[key].name + "</option>");
            $("#assign_user").append('<option value="' + key + '" >' + obj[key].name + "</option>");
        }
    });
    $(document).on("click", ".custom", function (e) {
        var self = this;
        var values = $(this).attr("data-res_ids");
        $.ajax({
            url: "/open-ticket",
            data: { ids: values },
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
            },
        });
    });

    $(document).on("change", "#days_filter", function (e) {
        var filter_date = $("#days_filter").children("option:selected").val();
        if (filter_date == "custom") {
            $("#start_date").removeClass("o_hidden");
            $("#end_date").removeClass("o_hidden");
        } else {
            $("#start_date").addClass("o_hidden");
            $("#end_date").addClass("o_hidden");
            $("#start_date").val("");
            $("#end_date").val("");
        }
        $.get(
            "/get-ticket-table-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_tbl_div").replaceWith(result);
            }
        );
        $.get(
            "/get-ticket-counter-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_count_div").replaceWith(result);
            }
        );
    });
    $(document).on("click", ".mark-whatsapp", function (e) {
        var $el = $(e.target).parents("tr").find("#partner_id").attr("value");
        var $mobile = $(e.target).parents("tr").find("#partner_id").attr("data-mobile");
        var partner_id = parseInt($el);
        $(".whatsapp_modal").modal("show");
        $("#ticket_partner_id").val(partner_id);
        $("#partner_mobile_no").val($mobile);
    });
    $(document).on("change", "#ticket_partner_id", function (e) {
        $.ajax({
            url: "/get-mobile-no",
            data: { 'partner_id': $('#ticket_partner_id').val() },
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                if (datas.mobile) {
                    $("#partner_mobile_no").val(datas.mobile);
                }
            },
        });
    });
    $(document).on("click", "#send", function (e) {
        $.ajax({
            url: "/send-by-whatsapp",
            data: { 'partner_id': $('#ticket_partner_id').val(), 'partner_mobile_no': $('#partner_mobile_no').val(), 'message': $('#whatsapp_message').val() },
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                if (datas.msg) {
                    alert(datas.msg);
                }
                else {
                    if (datas.url) {
                        window.open(datas.url, '_blank');
                    }
                }
            },
        });
    });
    $(document).on("change", "#assign_user", function (e) {
        $.get(
            "/get-ticket-table-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_tbl_div").replaceWith(result);
            }
        );
        $.get(
            "/get-ticket-counter-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_count_div").replaceWith(result);
            }
        );
    });
    $(document).on("change", "#start_date", function (e) {
        $.get(
            "/get-ticket-table-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_tbl_div").replaceWith(result);
            }
        );
        $.get(
            "/get-ticket-counter-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_count_div").replaceWith(result);
            }
        );
    });
    $(document).on("change", "#end_date", function (e) {
        $.get(
            "/get-ticket-table-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_tbl_div").replaceWith(result);
            }
        );
        $.get(
            "/get-ticket-counter-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_count_div").replaceWith(result);
            }
        );
    });
    $(document).on("change", "#team_leader", function (e) {
        $.ajax({
            url: "/get-leader-user",
            data: { team_leader: $("#team_leader").val() },
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                $("#team > option").remove();
                $("#team").append('<option value="0">Team</option>');
                for (var key in datas) {
                    $("#team").append('<option value="' + key + '" >' + datas[key].name + "</option>");
                }
            },
        });
        $.get(
            "/get-ticket-table-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_tbl_div").replaceWith(result);
            }
        );
        $.get(
            "/get-ticket-counter-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_count_div").replaceWith(result);
            }
        );
    });
    $(document).on("change", "#team", function (e) {
        $.ajax({
            url: "/get-user",
            data: { team: $("#team").val() },
            type: "post",
            cache: false,
            success: function (result) {
                var datas = JSON.parse(result);
                $("#assign_user > option").remove();
                $("#assign_user").append('<option value="0" selected="True">Assign User</option>');
                for (var key in datas) {
                    $("#assign_user").append('<option value="' + key + '" >' + datas[key].name + "</option>");
                }
            },
        });
        $.get(
            "/get-ticket-table-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_tbl_div").replaceWith(result);
            }
        );
        $.get(
            "/get-ticket-counter-data",
            {
                team: $("#team").val(),
                team_leader: $("#team_leader").val(),
                user_id: $("#assign_user").val(),
                filter_date: $("#days_filter").children("option:selected").val(),
                date_start: $("#start_date").val(),
                date_end: $("#end_date").val(),
            },
            function (result) {
                $("#js_ticket_count_div").replaceWith(result);
            }
        );
    });
});
