$(function () {
    var $progress = $("#progress-bar");
    var filebox = $("#mybox").yupload({
        btnText: '浏览',
        maxSize: 1024 * 1024 * 10,//10M
        url: '/process_image',
        onUpload: function (p) {
            $progress.width(p + '%').children(".sr-only").text(p + "% Complete");
        }
    });

    $("#upload_button").on("click", function (e) {
        $("#show_tips").show();
        $("#result_show").hide();
        $("#result_list").html("");
        filebox.submitUpload();
    });
});

jQuery.fn.extend({
    yupload: function (config) {
        var def = {
            btnText: '浏览...',      //按钮的文本
            accept: '*',              //选择的文件类型
            maxSize: 1024 * 1024,       //单个文件大小
            multiple: true,            //是否上传多个文件
            url: '',               //提交的地址
            method: "POST",           //提交的方式

            onSubmit: function (v) {
            },    //提交到制定服务后的回调事件；参数为服务端返回的参数
            onSelect: function (l) {
            },    //选择文件后触发的事件；参数为选择的文件列表
            onUpload: function (p) {
            }    //上传文件时，出发的事件；参数为当前的进度
        };
        config = $.extend({}, def, config);
        /* ============变量============ */
        var $this = $(this);
        var PENDING_FILES = []; //文件列表
        var $file = document.createElement("input");
        // $btn = document.createElement("input");
        /* ============自定义方法============ */
        var setStyle = function () {
                $this.addClass("file-box");

                $file.id = 'upload_file';
                $file.type = 'file';
                $file.accept = config.accept;
                $file.className = "file-file";
                if (config.multiple) $file.setAttribute("multiple", "multiple");
                $this.append($file);
            },
            loadEvent = function () {
                var maxsize = config.maxSize;
                $file.onchange = function () {
                    var files = this.files;
                    var file_length = files.length;

                    if(file_length <= 0) {
                        return;
                    }

                    PENDING_FILES = [];

                    for (var i = 0, ie = file_length, item; i < ie; i++) {
                        item = files[i];
                        // 在这里做验证
                        if (item.size > maxsize) {
                            alert('大小超过配置的最大值！\n当前大小为：' + item.size + '\n要求的最大值为：' + maxsize);
                            $('#upload_file').val('');
                            return;
                        }
                        PENDING_FILES.push(item);
                    }

                    config.onSelect(files);
                }
            },
            //提交上传
            submitUpload = function () {
                if (!config.url) {
                    config.onSubmit({error: '提交的URL地址错误'});
                    return;
                }
                var param = new FormData();
                // 绑定参数
                for (var i = 0, ie = PENDING_FILES.length; i < ie; i++) {
                    param.append("file", PENDING_FILES[i]);
                }

                var classify_code = $("#classify_code").val();
                param.append("classify_code",classify_code);
                var product_name = $("#product_name").val();
                param.append("product_name",product_name);

                var xhr = $.ajax({
                    xhr: function () {
                        var xhrobj = $.ajaxSettings.xhr();
                        if (xhrobj.upload) {
                            xhrobj.upload.addEventListener("progress", function (event) {
                                var percent = 0;
                                var position = event.loaded || event.position;
                                var total = event.total;
                                if (event.lengthComputable) {
                                    percent = Math.ceil(position / total * 100);
                                }
                                config.onUpload(percent);
                            }, false)
                        }
                        return xhrobj;
                    },
                    url: config.url,
                    method: config.method,
                    contentType: false,
                    processData: false,
                    data: param,
                    success: function (result_data, textStatus) {
                        if (textStatus) {
                            var json = JSON.parse(result_data);
                            var resultHtml = "";
                            var obj = json;
                            var result = obj.result;

                            if(result == 0){
                                var image_datas = obj.data;

                                var images = image_datas.images;
                                var titles = image_datas.titles;
                                var contents = image_datas.contents;
                                var product_name = image_datas.product_name;

                                resultHtml += "<div class=\"show-upload-item\">";
                                resultHtml += "<div class=\"file-name\"> 商品编码: " + product_name + "</div>";
                                resultHtml += "<div class=\"upload-item\">";
                                resultHtml += "<div class=\"col-lg-6\">";

                                for(var item in images) {
                                    resultHtml += "<img src='" + images[item] + "' />";
                                }
                                resultHtml += "</div>";
                                resultHtml += "<div class=\"ocr-show col-lg-6\">";

                                for(var index in titles){
                                    resultHtml += "<p>" + titles[index] + ":\t" + contents[index] + "</p>";
                                }

                                resultHtml += "</div>";
                                resultHtml += "</div>";
                                resultHtml += "</div>";

                                $("#ocr_show_tips").hide();
                                $("#ocr_result_list").html(resultHtml);
                                $("#ocr_result_show").show();
                            }else{
                                alert("解析图片失败");
                                $("#show_tips").hide();
                                }
                            PENDING_FILES = [];
                            $('#ocr_progress-bar').width('0%').children(".sr-only").text("0% Complete");
                        } else {
                            alert("解析图片失败");
                            $("#show_tips").hide();
                        }
                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        config.onSubmit({error: XMLHttpRequest});
                    }
                });
            };
        setStyle();
        loadEvent();
        return {
            submitUpload: submitUpload,
            getFiles: PENDING_FILES
        }
    }
});