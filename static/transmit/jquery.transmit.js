/**
 * jQuery Transmit plugin (http://code.google.com/p/jquery-transmit)
 *
 * Copyright (c) 2008-2009 Carl Sziebert, Paul Gregoire
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
;(function($) {

    $.transmit = {
        defaults: {
            allowedDomain: location.hostname,
            allowedFileTypes: {}, // Any file type.
            debug: false,
            maxFileSize: 5242880, // 5 MB in bytes
            swfId: 'transmit',
            swfUrl: 'uploader.swf'
        },
        files: {},
        isUploading: false,
        numFiles: 0,
        numFilesCompleted: 0,
        settings: null,
        swf: null,
        uploadUrl: ''
    };
    
    /* ----- API functions ----- */

    $.fn.extend({

        /**
         * Instantiate the uploader, embed the SWF.
         *
         * @param uploadUrl <p>the url to upload selected files to</p>
         * @param settings <p>convenience object to override the default settings<p>
         */
        transmit: function(uploadUrl, settings) {
            var containerId = $(this).attr('id');
            $.transmit.uploadUrl = uploadUrl;
            $.transmit.settings = $.extend({}, $.transmit.defaults, settings);
            var attributes = {
                id: $.transmit.settings.swfId,
                data: $.transmit.settings.swfUrl,
                width: '100%',
                height: '100%'
            };
            var params = {
                allowedDomain: $.transmit.settings.allowedDomain,
                allowscriptaccess: 'always',
                bgcolor: "#FF0000",
                flashvars:'elementId=' + containerId + '&eventHandler=$.fn.eventDispatcher',
                menu: "false",
                wmode: "transparent"
            };
            $.transmit.swf = swfobject.createSWF(attributes, params, containerId);
            if ($.transmit.swf) {
                $.transmit.swf.owner = this;
            }
            return this.each(function() {
                $.data(this, 'transmit', settings);
            });
        },

        /**
         * Upload the selected files.
         *
         * @param params <p>Additional variables sent to the upload url along with the files</p>
         */
        upload: function(params) {
            $.transmit.isUploading = true;
            $('div.messages').find('div').addClass('hidden');
            $.transmit.swf.uploadAll($.transmit.uploadUrl, 'POST', params);
            $('#upload-table div.header div.status').html('');
            var rows = $('#file-list').find('li').get();
            $.each(rows, function(index, row) {
                if (!$(row).is('.hidden')) {
                    $(row).find('div.status').html('');
                }
            });
            $('#uploadBtn').attr('disabled', 'disabled').attr('value', 'Uploading...');
            $('#upload-add-more').addClass('hidden');
        },

        /**
         * Cancel the upload of a specific file.
         *
         * @param fileId <p>the file to cancel</p>
         */
        cancel: function(fileId) {
            $.transmit.swf.cancel(fileId);
            $.fn.removeFile(fileId);
        },

        /**
         * Reset the uploader.
         */
        clearFileList: function() {
            $.transmit.isUploading = false;
            $.transmit.swf.clearFileList();
            $.transmit.fileCount = 0;
            $('div.step1').removeClass('hidden');
            $('div.step2').addClass('hidden');
            $('div.messages').find('div').addClass('hidden');
            var step = $('a.upload-add-files');
            var offset = step.position();
            moveSwf(offset.top, offset.left, step.width(), step.height());
        },

        /**
         * Remove the speficied file from the upload queue.
         *
         * @param fileId <p>the file to be removed</p>
         */
        removeFile: function(fileId) {
            if ($.transmit.files[fileId]) {
                $.transmit.swf.removeFile(fileId);
                $('#'+fileId).remove();
                delete $.transmit.files[fileId];
                $.transmit.numFiles--;
                if ($.transmit.numFiles > 0) {
                    renderFileTotals();
                } else {
                    $.fn.clearFileList();
                }
            }
        },

        /**
         * Handle events sent to the plugin from the embedded SWF.
         *
         * @param elementId <p>the wrapping div</p>
         * @param event <p>the event to be processed</p>
         */
        eventDispatcher: function(elementId, event) {
            //console.debug("elementId: %s, event: %o", elementId, event);
            if (event && event.type) switch(event.type) {
                case 'swfReady':
                    onSwfReady(event);
                    break;
                case 'fileSelect':
                    onFileSelect(event);
                    break;
                case 'uploadStart':
                    onUploadStart(event);
                    break;
                case 'uploadProgress':
                    onUploadProgress(event);
                    break;
                case 'uploadCancel':
                    onUploadCancel(event);
                    break;
                case 'uploadComplete':
                    onUploadComplete(event);
                    break;
                case 'uploadCompleteData':
                    onUploadCompleteData(event);
                    break;
                case 'uploadError':
                    onUploadError(event);
                    break;
                case 'log':
                    onSwfDebug(event);
                    break;
            }
        }
    });
    
    /* ----- Event handlers ----- */
        
    function onSwfReady(event) {
        $('#step1').find('h3').wrapInner('<a class="upload-add-files" href="javascript:void(0);"></a>');
        var step = $('a.upload-add-files');
        var offset = step.position();
        moveSwf(offset.top, offset.left, step.width(), step.height());
        $.transmit.swf.setAllowMultipleFiles(true);
        $.transmit.swf.setFileFilters($.transmit.settings.allowedFileTypes);
        $('#uploadBtn').attr('disabled', '').click(function() {
            $.fn.upload();
        });
    }
    
    function onFileSelect(event) {
        $.each(event.fileList, function(id, file) {
            $.transmit.files[id] = file;
            $.transmit.numFiles++;
        });
        renderFileList();
    }
    
    function onUploadStart(event) {
        // Do nothing...
    }

    function onUploadProgress(event) {
        var percent = Math.round((event.bytesLoaded / event.bytesTotal * 100));
        $('#' + event.id).find('div.status').html(percent + '%');
    }

    function onUploadCancel(event) {
        // Do nothing...
    }

    function onUploadComplete(event) {
        $.transmit.numFilesCompleted++;
        var elem = $('#' + event.id);
        elem.find('div').addClass('disabled');
        elem.find('div.status').empty().html('<a class="complete" title="Upload complete">&nbsp;</a>');
        if ($.transmit.isUploading && $.transmit.numFiles == $.transmit.numFilesCompleted) {
            $('div.success').removeClass('hidden');
            $('div.buttons').addClass('hidden');
            moveSwf(0, -9999, 1, 1);
        }
    }

    function onUploadCompleteData(event) {
        // Do nothing...
    }

    function onUploadError(event) {
        $('#' + event.id).find('div.status').empty().html('<a class="error" title="' + event.status + '">&nbsp;</a>');
        $('div.error').removeClass('hidden');
        $('#uploadBtn').removeAttr('disabled').attr('value', 'Upload Files');
    }

    function onSwfDebug(event) {
        // Log to firebug when available.
        if ($.transmit.settings.debug && window.console && window.console.firebug) {
            console.debug('[SWF]: %o', event);
        }
    }
    
    /* ----- Utility functions ----- */
    
    function renderFileList() {
        resetFileList();
        var rows = [];
        $.each($.transmit.files, function(id, file) {
            var row = $('#row-template').clone().attr('id', id).removeClass('hidden');
            row.find('div.name').html(file.name);
            row.find('div.size').html(formatFileSize(file.size));
            if (file.size > $.transmit.settings.maxFileSize) {
                row.addClass('overlimit');
                $('div.overlimit').removeClass('hidden');
            }
            row.find('a.remove').attr('title', 'Remove ' + file.name + '?').click(function() {
                $.fn.removeFile(id);
            });
            rows.push(row);
        });
        sortFileList(rows);
        $.each(rows, function(index, row) {
            row.insertBefore('#row-template');
        });
        $('div.step1').addClass('hidden');
        $('div.step2').removeClass('hidden');
        var step = $('a.upload-add-more');
        var offset = step.position();
        moveSwf(offset.top, offset.left, step.width(), step.height());
        renderFileTotals();
    }

    function moveSwf(top, left, width, height) {
        $('#transmit-uploader').css('top', top).css('left', left).width(width).height(height);
    }
    
    function resetFileList() {
        var rows = $('#file-list').find('li').get();
        $.each(rows, function(index, row) {
            if (!$(row).is('.hidden')) {
                $(row).remove();
            }
        });
    }
    
    function renderFileTotals() {
        $.transmit.numFiles = 0;
        var totalSize = 0;
        $.each($.transmit.files, function(id, file) {
            totalSize += file.size;
            $.transmit.numFiles++;
        });
        if ($.transmit.numFiles == 1) {
            $('#upload-file-count').html($.transmit.numFiles + ' File');
        } else {
            $('#upload-file-count').html($.transmit.numFiles + ' Files');
        }
        $('#upload-total-bytes').html('Total: ' + formatFileSize(totalSize));
    }
    
    function formatFileSize(fileSize) {
        var suffix = 'KB';
        var size = Number(fileSize);
        if (size >= 1048576) {
            size = size / 1048576;
            suffix = 'MB';
        } else {
            size = size / 1024;
        }
        return size.toFixed(2).toString() + ' ' + suffix;
    }
    
    function sortFileList(rows) {
        rows.sort(function(a, b) {
            var nameA = $(a).children('div.name').text().toLowerCase();
            var nameB = $(b).children('div.name').text().toLowerCase();
            if (nameA < nameB) { 
                return -1;
            }
            if (nameA > nameB) {
                return 1;
            }
            return 0;
        });
    }
    
})(jQuery);