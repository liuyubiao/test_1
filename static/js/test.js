$(function () {
    // 进入页面时首先执行加载操作
    // 1. 加载支持品类及功能
     $("#open_close_table").on("click",function () {
        // 判断table的属性
        var state = $("#result").css("display");

        if(state == "none"){
            $("#result").css("display","");
            $("#open_close_table").html("结果收起");
        } else {
            $("#result").css("display","none");
            $("#open_close_table").html("结果展开");
        }
    });

    // 2. 加载各品类的测试结果及准确率
    var testHtml = "";
    // var data_list = [['101', '水果', '100', '0.96 ', '0.80'], ['102', '蔬菜', '100', '0.92 ', '0.83'], ['103', '蛋类', '100', '0.90 ', '0.89'], ['104', '生肉', '100', '0.95 ', '0.94'], ['106', '水产品', '100', '0.91 ', '0.88'], ['112', '黄油蜂蜜', '100', '0.96 ', '0.95'], ['114', '口香糖', '100', '0.94 ', '0.92'], ['117', '营养粉', '100', '0.94 ', '0.93'], ['121', '香肠', '100', '0.92 ', '0.92'], ['125', '膨化食品', '100', '0.90 ', '0.88'], ['126', '海苔', '100', '0.94 ', '0.89'], ['127', '沙琪玛烤芙条', '100', '0.95 ', '0.91'], ['128', '酱油', '100', '0.96 ', '0.93'], ['129', '果冻布丁(嗜喱)', '100', '0.94 ', '0.94'], ['130', '食醋', '100', '0.96 ', '0.95'], ['131', '中式酱', '100', '0.98 ', '0.94'], ['133', '面包', '100', '0.95 ', '0.93'], ['134', '蛋糕', '100', '0.95 ', '0.94'], ['137', '方便食品', '100', '0.92 ', '0.91'], ['139', '饼干', '100', '0.93 ', '0.91'], ['159', '牛奶', '100', '0.92 ', '0.90'], ['299', '白酒', '100', '0.97 ', '0.95'], ['148', '冰淇淋', '100', '0.92 ', '0.88'], ['149', '速冻食品', '100', '0.93 ', '0.90'], ['189', '食用植物油', '100', '0.89 ', '0.86'], ['191', '面粉', '100', '0.93', '0.91'], ['315', '洗发水洗发膏', '100', '0.88', '0.88'], ['316', '护发素', '100', '0.90', '0.90'], ['323', '香水', '100', '0.86', '0.86'], ['342', '杀虫驱蚊剂', '100', '0.91', '0.91']]
    // var data_list = [['101', '水果', '100', '0.97'], ['102', '蔬菜', '100', '0.96'], ['103', '蛋类', '100', '0.91'], ['104', '生肉', '100', '0.96'], ['106', '水产品', '100', '0.92'], ['112', '黄油蜂蜜', '100', '0.96'], ['114', '口香糖', '100', '0.95'], ['117', '营养粉', '100', '0.96'], ['121', '香肠', '100', '0.93'], ['125', '膨化食品', '100', '0.92'], ['126', '海苔', '100', '0.89'], ['127', '沙琪玛烤芙条', '100', '0.91'], ['128', '酱油', '100', '0.93'], ['129', '果冻布丁(嗜喱)', '100', '0.94'], ['130', '食醋', '100', '0.95'], ['131', '中式酱', '100', '0.84'], ['133', '面包', '100', '0.91'], ['134', '蛋糕', '100', '0.91'], ['137', '方便食品', '100', '0.82'], ['139', '饼干', '100', '0.93'], ['148', '冰淇淋', '100', '0.92'], ['149', '速冻食品', '100', '0.93'], ['159', '牛奶', '100', '0.89'], ['189', '食用植物油', '100', '0.89'], ['191', '面粉', '100', '0.93'], ['299', '白酒', '100', '0.90'], ['315', '洗发水洗发膏', '100', '0.88'], ['316', '护发素', '100', '0.90'], ['323', '香水', '100', '0.86'], ['342', '杀虫驱蚊剂', '100', '0.91']]
    var data_list = [['101', '水果', '100', '0.97'], ['102', '蔬菜', '100', '0.96'], ['103', '蛋类', '100', '0.91'], ['104', '生肉', '100', '0.96'], ['106', '水产品', '100', '0.92'], ['112', '黄油蜂蜜', '100', '0.96'], ['114', '口香糖', '100', '0.95'], ['117', '营养粉', '100', '0.96'], ['121', '香肠', '100', '0.93'], ['125', '膨化食品', '100', '0.92'], ['126', '海苔', '100', '0.89'], ['127', '沙琪玛烤芙条', '100', '0.91'], ['128', '酱油', '100', '0.93'], ['129', '果冻布丁(嗜喱)', '100', '0.94'], ['130', '食醋', '100', '0.95'], ['131', '中式酱', '100', '0.84'], ['133', '面包', '100', '0.91'], ['134', '蛋糕', '100', '0.91'], ['138', '中式点心', '100', '0.93'], ['139', '饼干', '100', '0.93'], ['148', '冰淇淋', '100', '0.92'], ['149', '速冻食品', '100', '0.93'], ['159', '牛奶', '100', '0.89'], ['189', '食用植物油', '100', '0.89'], ['191', '面粉', '100', '0.93'],  ['217', '鸡尾酒/洋酒/果酒/露酒', '100', '0.92'], ['218', '葡萄酒', '100', '0.94'], ['223', '固体茶类', '100', '0.94'], ['230', '碳酸饮料', '100', '0.93'], ['232', '果汁饮料', '100', '0.92'], ['235', '包装饮用水', '100', '0.94'], ['295', '啤酒', '100', '0.94'], ['299', '白酒', '100', '0.90'], ['315', '洗发水洗发膏', '100', '0.95'], ['316', '护发素', '100', '0.96'], ['323', '香水', '100', '0.97'], ['342', '杀虫驱蚊剂', '100', '0.95'], ['429', '卫生巾', '100', '0.94'], ['492', '保鲜膜袋', '100', '0.94'], ['507', '香辛料', '100', '0.93'], ['510', '果干', '100', '0.97'], ['821', '婴儿纸尿裤', '100', '0.94'], ['827', '婴儿食品', '100', '0.95']]


    for(var i in data_list) {
        testHtml += "<tr>";
        var infos = data_list[i];
        for(var j in infos) {
            var item = infos[j];
            if(j == 1) {
                testHtml += "<td class=\"col-md-7\">" + item + "</td>";
            } else {
                testHtml += "<td class=\"col-md-1\">" + item + "</td>";
            }
        }
        testHtml += "</tr>";
    }
    $("#resultList").html(testHtml);

    // 3. 加载测试页面的图像数据,并调用识别得到测试结果
    // var image_list = ["../static/images/126_1.jpg","../static/images/126_2.jpg","../static/images/126_3.jpg","../static/images/126_4.jpg"];
    // 初始化图片
    // load_image(image_list);
    // 初始化结果
    $("#show_result").html("");
    load_init_result();

    const canvas = document.getElementById("image_canvas");
    const ctx = canvas.getContext('2d');

    // 完全加载完毕之后发送请求
    var url = "/process_image";
    // 以下为交互事件
    // 选择文件触发事件
    $("#file").change(function () {
        var classify_code = $("#classify_code").val();

		var files = this.files;
        var file_length = files.length;

        if(file_length <= 0) {
            console.log("未选中图片");
            return;
        }

        // 开始调用识别操作
        get_recognize(classify_code, files);
    });

    function load_image(image_list) {
        var tmpHtml = "";
        for(var i in image_list){
            if(i > 4) {
                break;
            }
            var image_path = image_list[i];
            if(i == 0){
                tmpHtml += "<div class=\"image-select-item\"><img src=\"" + image_path + "\"></div>";
                // canvas加载大图
                canvas_draw_image(image_path)
            } else {
                tmpHtml += "<div class=\"image-select-item\"><img src=\"" + image_path + "\"></div>";
            }
        }
        $("#image_list").html(tmpHtml);
    }

    // 为img添加点击操作
    $("#image_list").on('click', 'img',function() {
        canvas_draw_image(this.src);
    });

    function canvas_draw_image(image_path) {
        var image = new Image();
        image.src = image_path;

        image.onload = function () {
            ctx.drawImage(this, 0, 0, 1680, 1048);
        };
    }

    function get_recognize(category_id, files) {
        // 先去除背景图片
        ctx.clearRect(0, 0, 1680, 1048);

        $(".demo-loading").css("display","block");
        $(".tech-recognition-scan").css("display","block");

        var param = new FormData();
        // 绑定参数
        for (var i = 0, ie = files.length; i < ie; i++) {
            param.append("file", files[i]);
        }

        param.append("classify_code",category_id);
        var product_name = "";
        param.append("product_name",product_name);

        $.ajax({
            url: url,
            method: "post",
            contentType: false,
            processData: false,
            data: param,
            success: function (result_data, textStatus) {
                if (textStatus) {
                    var json = JSON.parse(result_data);
                    var tmpHtml = "<li class=\"result-item\"><span class=\"result-num result-title\">序号</span> <span class=\"result-text result-title\">内容</span></li>";

                    var result = json.result;
                    if(0 == result){
                        var data_infos = json.data;
                        var image_infos = data_infos.images;
                        var content_infos = data_infos.contents;
                        var title_infos = data_infos.titles;

                        for(var item in content_infos) {
                            var code = item;
                            var item_title = title_infos[item];
                            var item_content = content_infos[item];
                            if(item_content == "undefined"){
                                    item_content = "";
                            }
                            var show_content = item_title + ":" + item_content;
                            tmpHtml += "<li class=\"result-item\"><span class=\"result-num\">" + code + "</span> <span class=\"result-text\">" + show_content + "</span>";
                        }
                        // 加载图片
                        load_image(image_infos);

                        $("#show_result").html(tmpHtml);
                    } else {
                        alert("商品信息识别失败");
                        $("#show_result").html("");
                    }
                } else {
                    alert("商品信息识别失败");
                    $("#show_result").html("");
                }

                // $("#waiting_show").css('display','none');
                $(".demo-loading").css("display","none");
                $(".tech-recognition-scan").css("display","none");
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert("商品信息识别失败");
                $("#show_result").html("");

                // $("#waiting_show").css('display','none');
            }
        });
    }
    
    function load_init_result() {
        var json = {"data":{"contents":["126","海苔","0189a0e6-f23f-11ec-ac2a-6245b4ef3625","兔女王","不分","不分","90克","海蛋卷酥","咸蛋黄味","铁桶","纯即食海苔","咸蛋黄、鸡蛋","非独立包装","卷"],"titles":["品类编码","品类名称","商品编码","品牌1","品牌2","重容量*数量","重容量","商品全称","口味","包装形式","类型","添加物","是否是独立装","形状"],"images":["static/images/126_1.jpg","static/images/126_2.jpg","static/images/126_3.jpg","static/images/126_4.jpg"],"product_name":"0189a0e6-f23f-11ec-ac2a-6245b4ef3625"},"result":0,"msg":"识别成功"};
        var tmpHtml = "<li class=\"result-item\"><span class=\"result-num result-title\">序号</span> <span class=\"result-text result-title\">内容</span></li>";

        var result = json.result;
        if(0 == result) {
            var data_infos = json.data;
            var image_infos = data_infos.images;
            var content_infos = data_infos.contents;
            var title_infos = data_infos.titles;

            for (var item in content_infos) {
                var code = item;
                var item_title = title_infos[item];
                var item_content = content_infos[item];
                if (item_content == "undefined") {
                    item_content = "";
                }
                var show_content = item_title + ":" + item_content;
                tmpHtml += "<li class=\"result-item\"><span class=\"result-num\">" + code + "</span> <span class=\"result-text\">" + show_content + "</span>";
            }
            // 加载图片
            load_image(image_infos);

            $("#show_result").html(tmpHtml);
        }
    }
});
