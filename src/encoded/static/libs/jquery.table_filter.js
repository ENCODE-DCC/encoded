/*
 * Table Filter (for jQuery)
 * version: 0.1.0 (Oct. 18, 2012)
 *
 * Licensed under the MIT:
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Copyright 2012 Efe Amadasun [ efeamadasun@gmail.com ]
 *
 * USAGE:
 *
 * <div class="f_tbl">
 * <input type="text" class="table-filter"/>
 * <table>...</table>
 * </class>
 *
 * $(function(){
 *   $(".f_tbl").table_filter();
 * });
 *
 * ADDITIONAL SETTINGS:
 *
 * filter_inverse (boolean) - default: False
 * True - filters out rows that match the filter text
 * False - filters out rows that do not match the filter text
 *
 * enable_space (boolean) - default: False
 * True - it uses space in filter text as delimiters. e.g. if filter text = "good boy", it
 *        will search rows for "good" and "boy" seperately
 * False - it will not use space as a delimiter. e.g. "good boy" will be treated as one word.
 *
 * filter_selector (string) - default: 'input.table-filter'
 * Allows override of the filter selector.
 *
 * cell_selector (string) - default: 'td'
 * Allows override of the cell selector, so that only certain cells will be filtered.
 * Example setting to only filter on the first column: {'cell_selector':'td:first-child'}
 *
 */

(function($){

	$.fn.table_filter = function (options) {

		//set default plugin values
		var settings = $.extend({

			'filter_inverse': false,
			'enable_space': false,
			'filter_selector': 'input.table-filter',
			'cell_selector': 'td'

		}, options);

		//return element, to maintain chainability
		return this.each(function () {
			var $this = $(this);
			var $tbody = $this.find('tbody:first');
			var $input = $this.find(settings.filter_selector);
			var $counter = $this.find('#table-count');

			$input.bind("keyup", function () {

				//set filter text, and filterable table rows
				var txt = $input.val().toLowerCase();
				var $rows = $tbody.children("tr");

				$rows.each(function () {
					//default visibilty for rows is set based on filter_inverse value
					var $row = $(this);
					var show_tr = (settings.filter_inverse) ? true : false;
					var $cells = $row.find(settings.cell_selector);

					$cells.each(function () {
						var $cell = $(this);
						var td_txt = $.trim($cell.text()).toLowerCase();

						//if space is enabled as a delimiter, split the TD text value
						//and check the individual values against the filter text.
						if(settings.enable_space){

							var td_array = txt.split(" ");
							$.each(td_array, function (i) {
								var td_value = td_array[i];

								if(td_txt.indexOf(td_value) != -1){
									show_tr = (settings.filter_inverse) ? false : true;
								}
							});

						}
						else{

							if(td_txt.indexOf(txt) != -1){
								show_tr = (settings.filter_inverse) ? false : true;
							}

						}

					});

					if(show_tr){
						$(this).show().removeClass('hidden');
					}
					else{
						$(this).hide().addClass('hidden');
					}

				});

				//display all rows if filter text is empty
				if($.trim(txt) === ""){
					$tbody.children("tr").show().removeClass('hidden');
				}

				$tbody.setoddeven();
				$counter.text(function(index, text) {
					return $tbody.children().not(".hidden").length;
                });


			});

		});

	};

})(jQuery);
